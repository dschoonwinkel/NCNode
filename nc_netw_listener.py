import threading
from nc_shared_state import SharedState
from pypacker.layer12 import ethernet, cope
import socket
import logging
import crc_funcs

import coding_utils

# If the nc_netw_listener is running on client, not switch,
# it listens directly from the network
class NetworkListenerHelper(threading.Thread):
    def __init__(self, sharedState, listener):
        threading.Thread.__init__(self)
        self.sharedState = sharedState
        self.listener = listener
        self.daemon = True
        self.logger = logging.getLogger('nc_node.NetworkListenerHelper')

    def run(self):
        listener_socket = None
        try: 
            listener_socket = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x003))
            self.sharedState.setNetworkSocket(listener_socket)        # If successful, save the network socket to sharedState
            # self.logger.debug("Starting networkInstance thread")

            while self.sharedState.run_event.is_set():
                packet = listener_socket.recvfrom(65565)

                # Get packet from tuple
                packet = packet[0]

                ether_pkt = ethernet.Ethernet(packet)  # TODO: Consider revising, using only bytes to filter


                if ether_pkt.type == cope.COPE_PACKET_TYPE and ether_pkt.src_s != self.sharedState.get_my_hw_addr():
                #     self.logger.debug("COPE packet received" )
                #     # self.logger.debug(ether_pkt.bin())
                    try:
                        self.listener.receivePkt(ether_pkt)
                    except:
                        self.logger.error("Error occured at receivePkt()")
                #     # print(coding_utils.print_hex("Raw packet", packet))
                    pass

            self.logger.debug("Stopping listener networkInstance graciously")
            if listener_socket:
                listener_socket.close()
                self.sharedState.setNetworkSocket(None)



        except socket.error as msg:
            self.logger.error('Socket could not be created. Error Code: ' + str(msg[0]) + ' Message ' + msg[1])
            if listener_socket:
                listener_socket.close()
                self.sharedState.setNetworkSocket(None)
        




class NetworkListener(object):

    def __init__(self, sharedState, acksReceipts, networkInstance=None):
        self.networkInstance = networkInstance
        self.sharedState = sharedState
        self.acksReceipts = acksReceipts
        self.logger = logging.getLogger('nc_node.NetworkListener')

        if networkInstance is None:
            # Create networkListenerHelper for listening
            self.networkInstance = NetworkListenerHelper(self.sharedState, self)
            self.sharedState.setRunEvent()
            self.networkInstance.start()

    def receivePkt(self, ether_pkt):
        self.logger.debug('Received packet from networkInstance')
        cope_pkt = ether_pkt[cope.COPE_packet]
        # print(ether_pkt[cope.COPE_packet])
        if cope_pkt:
            crcchecksum = crc_funcs.crc_checksum(cope_pkt._pack_header())
            if cope_pkt.checksum != crcchecksum:
                self.logger.debug("COPE packet bin() %s" % cope_pkt._pack_header())
                raise Exception("Invalid checksum for packet %d %d" %(cope_pkt.checksum, crcchecksum))

        else:
            # Packet does not contain a valid COPE packet
            return

        from_neighbour = ether_pkt.src_s

        # Check if overheard locally
        if from_neighbour == self.sharedState.get_my_hw_addr():
            self.sharedState.incrementPacketSeen()
        # Or received from network 
        else:
            self.sharedState.incrementPacketRecv()

        try:
            self.acksReceipts.processPkt(cope_pkt, from_neighbour)
        except:
            self.logger.error("Error occured at processPkt()")



def main():
    sharedState = SharedState()
    networkListener = NetworkListener(sharedState = sharedState)

if __name__ == '__main__':
    main()
