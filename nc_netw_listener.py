from scapy.all import *
import threading
import time
from nc_shared_state import SharedState
import COPE_packet_classes as COPE_classes
import logging
import coding_utils
# logging.basicConfig(format="%(asctime)-15s: %(message)s", level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
pkt_count = 0

# If the nc_netw_listener is running on client, not switch,
# it listens directly from the network
class NetworkListenerHelper(threading.Thread):
    def __init__(self, sharedState, listener):
        threading.Thread.__init__(self)
        self.sharedState = sharedState
        self.listener = listener
        self.daemon = True

    def run(self):
        global pkt_count
        listener_socket = None
        try: 
            listener_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x003))
            self.sharedState.setNetworkSocket(listener_socket)        # If successful, save the network socket to sharedState
            logging.debug("Starting networkInstance thread")

            while self.sharedState.run_event.is_set():
                packet = listener_socket.recvfrom(65565)
                # print threading.current_thread()

                # Get packet from tuple
                packet = packet[0]
                # print_hex("Raw packet", packet)

                scapy_pkt = Ether(packet)
                if scapy_pkt.type == COPE_classes.COPE_PACKET_TYPE and scapy_pkt.src != self.sharedState.get_my_hw_addr():
                    logging.debug("COPE packet received" )
                    self.listener.receivePkt(scapy_pkt)
                    # logging.debug("Packet count %d" % pkt_count)
                    pass

            logging.debug("Stopping listener networkInstance graciously")
            if listener_socket:
                listener_socket.close()
                self.sharedState.setNetworkSocket(None)



        except socket.error, msg:
            logging.error('Socket could not be created. Error Code: ' + str(msg[0]) + ' Message ' + msg[1])
            if listener_socket:
                listener_socket.close()
                self.sharedState.setNetworkSocket(None)
        




class NetworkListener(object):

    def __init__(self, sharedState, acksReceipts, networkInstance=None):
        self.networkInstance = networkInstance
        self.sharedState = sharedState
        self.acksReceipts = acksReceipts

        if networkInstance is None:
            # Create networkListenerHelper for listening
            self.networkInstance = NetworkListenerHelper(self.sharedState, self)
            self.sharedState.setRunEvent()
            self.networkInstance.start()

    def receivePkt(self, scapy_packet):
        logging.debug('Received packet from networkInstance')
        cope_pkt, cope_payload = coding_utils.extr_COPE_pkt(str(scapy_packet.payload))
        from_neighbour = scapy_packet.src

        # Check if overheard locally
        if from_neighbour == self.sharedState.get_my_hw_addr():
            self.sharedState.incrementPacketSeen()
        # Or received from network 
        else:
            self.sharedState.incrementPacketRecv()

        self.acksReceipts.processPkt(cope_pkt, from_neighbour)

        # Should we drop all packets, and resend them from our controller?
        # self.addACKsRecps.dropPkt(self.sharedState.pktid_to_bufferid[cope_pkt.encoded_pkts[0])

def main():
    sharedState = SharedState()
    networkListener = NetworkListener(sharedState = sharedState)

if __name__ == '__main__':
    main()