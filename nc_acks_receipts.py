import logging
import logging.config
import nc_shared_state
import COPE_packet_classes as COPE_classes
import threading
import time
import nc_transmitter
import coding_utils


class ACKsReceipts(object):

    def __init__(self, sharedState, decoder):
        self.sharedState = sharedState
        self.decoder = decoder
        logging.config.fileConfig('logging.conf')
        #self.#logger =logging.getLogger('nc_node.ACKsReceipts')

    def processPkt(self, cope_pkt, from_neighbour):
        #self.#logger.debug("Got packet to process acks")
        # cope_pkt.show2()
        # Extract the receipts and acks here
        # Pass the packet to the decoder
        # scapy_packet.show2()
        # cope_pkt.show2()
        
        if cope_pkt:
            for ack in cope_pkt.acks:
                #self.#logger.info("processing ACK %d" % ack.last_ack)
                self.sharedState.updateACKwaiters(ack, from_neighbour)

            for report in cope_pkt.reports:
                self.sharedState.updateRecpReports(report)

            self.decoder.decode(cope_pkt, from_neighbour)

        else:
            #self.#logger.error("Could not use COPE packet, probably incorrect packet format")
            pass


class AddACKsReceipts(object):

    def __init__(self, sharedState, transmitter):
        self.sharedState = sharedState
        self.transmitter = transmitter
        logging.config.fileConfig('logging.conf')
        #self.#logger =logging.getLogger('nc_node.AddACKsReceipts')

    def addACKsRecps(self, pkt):
        for i in range(len(self.sharedState.ack_queue)):
            ack = self.sharedState.popACKReport()
            #self.#logger.debug("Add pktno %d ack to packet", ack.last_ack)
            # Perform adding here
            pkt.acks = list()
            pkt.acks.append(ack)

        for i in range(len(self.sharedState.receipts_queue)):
            recp = self.sharedState.popRecpReport()
            #self.#logger.debug("Add pktno %d recp to packet", recp.last_pkt)
            
            pkt.reports = list()
            pkt.reports.append(recp)            
        
        
        # Increment neighbour seq nr here, schedule ack waiters 
        for encoded in pkt.encoded_pkts:
            self.sharedState.incrementNeighbourSeqnoSent(encoded.nexthop)
            ackwaiter = ACKWaiter(pkt, self.sharedState, self.transmitter)
            ackwaiter.start()
            self.sharedState.addACK_waiter(encoded.nexthop, self.sharedState.get_neighbour_seqnr_sent(encoded.nexthop), ackwaiter)
            
        # Local pkt seq no is the seq number of the first neighbour (possibly only) neighbour to which it is sent
        #self.#logger.debug("Encoded NUM %d" % len(pkt.encoded_pkts))
        if pkt.ENCODED_NUM >= 1:
            pkt.local_pkt_seq_no = self.sharedState.get_neighbour_seqnr_sent(pkt.encoded_pkts[0].nexthop) 


        #pkt.show2()
        ##self.#logger.critical(coding_utils.print_hex("Raw packet: ", str(pkt)))
        self.transmitter.transmit(pkt)

    
class ACKWaiter(threading.Thread):

    def __init__(self, pkt, sharedState, transmitter):
        threading.Thread.__init__(self)     
        self.pkt = pkt
        self.sharedState = sharedState
        self.stop_event = threading.Event()
        self.transmitter = transmitter              # Reference to transmitter is used to reschedule the transmission
        self.daemon = True
        logging.config.fileConfig('logging.conf')
        #self.#logger =logging.getLogger('nc_node.ACKWaiter')


    def stopWaiter(self):
        self.stop_event.set()


    def run(self):
        for i in range(self.sharedState.ack_retries):
            self.stop_event.wait(self.sharedState.ack_retry_time)
            if self.stop_event.is_set():
                #self.#logger.debug("ACKWaiter was stopped")
                return
            else:
                #self.#logger.debug("Resending packet %s", self.pkt.local_pkt_seq_num)
                self.transmitter.transmit(self.pkt)
                
        self.sharedState.incrementFailedACKs()

def main():
    sharedState = nc_shared_state.SharedState()
    transmitter = nc_transmitter.Transmitter(sharedState)
    pkt = COPE_classes.COPE_packet()
    waiter = ACKWaiter(pkt, sharedState, transmitter)
    waiter.start()
    time.sleep(3)
    waiter.stopWaiter()



if __name__ == '__main__':
    main()