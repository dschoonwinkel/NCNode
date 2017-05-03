import logging

logging.basicConfig(level=logging.DEBUG)
import network_utils


class Enqueuer(object):
    def __init__(self, sharedState, streamOrderer):
        self.streamOrderer = streamOrderer
        self.sharedState = sharedState
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('nc_node.ncEncoder')

    def enqueue(self, cope_packet):
        # Enqueue packet, or send to application layer if
        # final hop
        # Nexthop assignment should probably happen here...
        # based on some routing (Srcr) algorithm?
        # Currently, nexthop addresses are assigned according to previously heard packets, that is learned closest neighbours

        self.logger.debug("Got packet to enqueue")

        # Control packet
        if len(cope_packet.encoded_pkts) == 0:
            # Do not propogate control packets further than overheard hops
            return

        if len(cope_packet.encoded_pkts) > 1:
            self.logger.critical("Encoded packet lengths in enqueuer should not be longer than 1: %d" % len(cope_packet.encoded_pkts))
            raise Exception("Encoded packet lengths too long")

        # Steps for putting in stream orderer
        # 1. Check the encoded header, if it is meant for me, pass it to app layer, and stop forwarding
        if cope_packet.encoded_pkts[0].nexthop == self.sharedState.get_my_hw_addr():
            self.logger.debug("Packet sent to stream orderer")
            self.streamOrderer.order_stream(cope_packet)
            return

        # Steps for forwarding:
        # If it is a native packet, check IP address and forward to neighbour closest
        # self.logger.debug("Encoded NUM %d" % len(cope_packet.encoded_pkts))
        if len(cope_packet.encoded_pkts) == 1:
            self.logger.debug("Forwarding packet")

            # Check the IP dst address, if in sharedState dict, will use correct MAC address for forwarding
            ip_pkt = network_utils.check_IPPacket(str(cope_packet.payload))

            # If valid IP pkt, check address
            if ip_pkt:
                # 	If IP address known to us, i.e. closest neighbour known
                if ip_pkt.dst in self.sharedState.ip_to_mac:
                    dst_hw_addr = self.sharedState.getMACFromIP(ip_pkt.dst)
                    # Update nexthop, so that the next neighbour in the chain will process the packet
                    cope_packet.encoded_pkts[0].nexthop = dst_hw_addr
                    self.sharedState.addPacketToOutputQueue(dst_hw_addr, cope_packet)
                # If IP address is not know, forward to everyone
                else:
                    self.logger.error("IP dest not found in ip_to_mac for ip: %s" % ip_pkt.dst)
                    # self.sharedState.addPacketToOutputQueue(self.broadcast_HWAddr, cope_packet)
