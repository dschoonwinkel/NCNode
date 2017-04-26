import logging

logging.basicConfig(level=logging.DEBUG)
import network_utils


class Enqueuer(object):
    def __init__(self, sharedState, streamOrderer):
        self.streamOrderer = streamOrderer
        self.sharedState = sharedState
        self.broadcast_HWAddr = "ff:ff:ff:ff:ff:ff"

    def enqueue(self, cope_packet):
        # Enqueue packet, or send to application layer if
        # final hop
        # Nexthop assignment should probably happen here...
        # based on some routing (Srcr) algorithm?
        # Currently, nexthop addresses are assigned according to previously heard packets, that is learned closest neighbours

        logging.debug("Got packet to enqueue")

        # Steps for putting in stream orderer
        # 1. Check all the encoded headers, if it is meant for me, pass it to app layer, and stop forwarding
        for encoded_pkt in cope_packet.encoded_pkts:

            if encoded_pkt.nexthop == self.sharedState.get_my_hw_addr():
                logging.debug("Packet sent to stream orderer")
                self.streamOrderer.order_stream(cope_packet)
                return

        # Steps for forwarding:
        # If it is a native packet, check IP address and forward to neighbour closest
        logging.debug("Encoded NUM %d" % len(cope_packet.encoded_pkts))
        if len(cope_packet.encoded_pkts) == 1:
            logging.debug("Forwarding packet")

            # Check the IP dst address, if in sharedState dict, will use correct MAC address for forwarding
            ip_pkt = network_utils.check_IPPacket(str(cope_packet.payload))

            # If valid IP pkt, check address
            if ip_pkt:
                # 	If IP address known to us, i.e. closest neighbour known
                if ip_pkt.dst in self.sharedState.ip_to_mac:
                    dst_hw_addr = self.sharedState.ip_to_mac(ip_pkt.dst)
                    self.sharedState.addPacketToOutputQueue(dst_hw_addr, cope_packet)
                # If IP address is not know, forward to everyone
                else:
                    self.sharedState.addPacketToOutputQueue(self.broadcast_HWAddr, cope_packet)

        # Else (i.e. encoded or control msg), forward to everyone
        else:
            self.sharedState.addPacketToOutputQueue(self.broadcast_HWAddr, cope_packet)
