import logging
import logging.config
import nc_shared_state
import threading
import time
import nc_transmitter
import coding_utils
from pypacker.layer12 import cope
logging.config.fileConfig('logging.conf')
import asyncio

class ACKsReceipts(object):

    def __init__(self, sharedState, decoder):
        self.sharedState = sharedState
        self.decoder = decoder
        self.logger =logging.getLogger('nc_node.ACKsReceipts')

    def processPkt(self, cope_pkt, from_neighbour):
        self.logger.debug("Got packet to process acks")
        
        if cope_pkt:
            for ack in cope_pkt.acks:
                self.logger.info("processing ACK %d" % ack.last_ack)
                self.sharedState.updateACKwaiters(ack, from_neighbour)

            for report in cope_pkt.reports:
                self.sharedState.updateRecpReports(report)

            self.decoder.decode(cope_pkt, from_neighbour)

        else:
            self.logger.error("Could not use COPE packet, probably incorrect packet format")
            pass

class AddACKsReceipts(object):

    def __init__(self, sharedState, transmitter):
        self.sharedState = sharedState
        self.transmitter = transmitter

        self.logger =logging.getLogger('nc_node.AddACKsReceipts')

    def addACKsRecps(self, pkt):

        self.sharedState.times["AddACKs processed1"].append(time.time())

        for i in range(len(self.sharedState.ack_queue)):
            ack = self.sharedState.popACKReport()
            self.logger.debug("Add pktno %d ack to packet", ack.last_ack)
            # Perform adding here
            # pkt.acks = list()
            pkt.acks.append(ack)

        self.sharedState.times["AddACKs processed2"].append(time.time())

        for i in range(len(self.sharedState.receipts_queue)):
            recp = self.sharedState.popRecpReport()
            self.logger.debug("Add pktno %d recp to packet", recp.last_pkt)
            
            # pkt.reports = list()
            pkt.reports.append(recp)

        self.sharedState.times["AddACKs processed3"].append(time.time())

        # Increment neighbour seq nr here, schedule ack waiters
        # self.logger.debug(pkt.bin())
        for encoded in pkt.encoded_pkts:
            self.sharedState.incrementNeighbourSeqnoSent(encoded.nexthop_s)             # TODO : 7 us
            ackwaiter = ACKWaiter(pkt, self.sharedState, self.transmitter, self.sharedState.event_loop)              # TODO : 32 us
            ackwaiter.run()                                                           # TODO : 8 ms
            self.sharedState.addACK_waiter(encoded.nexthop_s,
                                           self.sharedState.get_neighbour_seqnr_sent(encoded.nexthop_s), ackwaiter) #TODO 12 us

        self.sharedState.times["AddACKs processed4"].append(time.time())
        # Local pkt seq no is the seq number of the first neighbour (possibly only) neighbour to which it is sent
        self.logger.debug("Encoded NUM %d" % len(pkt.encoded_pkts))

        if pkt.encoded_num >= 1:
            pkt.local_pkt_seq_num = self.sharedState.get_neighbour_seqnr_sent(pkt.encoded_pkts[0].nexthop_s)

        #pkt.show2()
        #self.logger.critical(coding_utils.print_hex("Raw packet: ", str(pkt)))

        self.sharedState.times["AddACKs processed"].append(time.time())
        self.transmitter.transmit(pkt)

    
class ACKWaiter(object):

    def __init__(self, pkt, sharedState, transmitter, event_loop):
        threading.Thread.__init__(self)     
        self.pkt = pkt
        self.sharedState = sharedState
        self.stop_event = threading.Event()
        self.transmitter = transmitter              # Reference to transmitter is used to reschedule the transmission
        self.event_loop = event_loop
        self.logger =logging.getLogger('nc_node.ACKWaiter')


    def stopWaiter(self):
        self.stop_event.set()


    def run(self):
        self.event_loop.call_later(self.sharedState.ack_retry_time, self.retry_reschedule, 0)

    def retry_reschedule(self, iters):
        if iters < self.sharedState.ack_retries:
            if self.stop_event.is_set():
                self.logger.debug("ACKWaiter was stopped")
                return
            else:
                self.logger.debug("Resending packet %s", self.pkt.local_pkt_seq_num)
                self.transmitter.transmit(self.pkt)
                self.event_loop.call_later(self.sharedState.ack_retry_time,self.retry_reschedule, iters+1)

        else:
            self.sharedState.incrementFailedACKs()



def main():
    sharedState = nc_shared_state.SharedState()
    transmitter = nc_transmitter.Transmitter(sharedState)
    pkt = cope.COPE_packet()
    event_loop = asyncio.get_event_loop()
    sharedState.event_loop = event_loop


    waiter = ACKWaiter(pkt, sharedState, transmitter, event_loop)
    waiter.start()
    time.sleep(3)

    try:
        print("ACKWaiter running, use Ctrl+C to kill program")
        event_loop.run_forever()
    except:
        waiter.stopWaiter()
        event_loop.close()



if __name__ == '__main__':
    main()
