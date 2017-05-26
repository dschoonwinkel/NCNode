import logging

import network_utils
import coding_utils


class Enqueuer(object):
    def __init__(self, sharedState, streamOrderer):
        self.streamOrderer = streamOrderer
        self.sharedState = sharedState
        logging.config.fileConfig('logging.conf')
        #self.#logger =logging.getLogger('nc_node.ncEnqueuer')

    def enqueue(self, cope_packet):
        # Enqueue packet, or send to application layer if
        # final hop
        # Nexthop assignment should probably happen here...
        # based on some routing (Srcr) algorithm?
        # Currently, nexthop addresses are assigned according to previously heard packets, that is learned closest neighbours

        #self.#logger.debug("Got packet to enqueue")
        # #self.#logger.debug("Encoded NUM %d" % len(cope_packet.encoded_pkts))

        # Control packet
        if len(cope_packet.encoded_pkts) == 0:                                              # TODO: 3.22 us
            # Do not propogate control packets further than overheard hops
            return

        if len(cope_packet.encoded_pkts) > 1:                                               # TODO: 2.66 us
            #self.#logger.critical("Encoded packet lengths in enqueuer should not be longer than 1: %d" % len(cope_packet.encoded_pkts))
            raise Exception("Encoded packet lengths too long")

        # Steps for putting in stream orderer
        # 1. Check the encoded header, if it is meant for me, pass it to app layer, and stop forwarding
        if cope_packet.encoded_pkts[0].nexthop == self.sharedState.get_my_hw_addr():        # TODO: 6 us
            #self.#logger.debug("Packet sent to stream orderer")
            self.streamOrderer.order_stream(cope_packet)
            return

        # Steps for forwarding:
        # If it is a native packet, check IP address and forward to neighbour closest

        if len(cope_packet.encoded_pkts) == 1:                                                  # TODO: 3.5 us
            #self.#logger.debug("Forwarding packet")

            # Check the IP dst address, if in sharedState dict, will use correct MAC address for forwarding
            ip_pkt = network_utils.check_IPPacket(str(cope_packet.payload))                     # TODO: 1.5 us

            # If valid IP pkt, check address
            if ip_pkt:                                                                          # TODO: 77 ns
                # 	If IP address known to us, i.e. closest neighbour known
                if ip_pkt.dst in self.sharedState.ip_to_mac:                                    # TODO 5.5 us
                    dst_hw_addr = self.sharedState.getMACFromIP(ip_pkt.dst)                     # TODO 6.5 us
                    # Update nexthop, so that the next neighbour in the chain will process the packet
                    cope_packet.encoded_pkts[0].nexthop = dst_hw_addr                           # TODO 12.5 us
                    self.sharedState.addPacketToOutputQueue(dst_hw_addr, cope_packet)           # TODO 1.7 us
                    # cope_packet.show2()                                                       # TODO 2.7 ms
                # If IP address is not know, forward to everyone
                else:
                    #self.#logger.error("IP dest not found in ip_to_mac for ip: %s" % ip_pkt.dst)
                    raise Exception("IP dest not found in ip_to_mac for ip: %s" % ip_pkt.dst)
                    # self.sharedState.addPacketToOutputQueue(self.broadcast_HWAddr, cope_packet)
