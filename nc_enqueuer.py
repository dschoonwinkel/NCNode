import logging
import time
import network_utils
from pypacker.layer3 import ip
logging.config.fileConfig('logging.conf')

class Enqueuer(object):
    def __init__(self, sharedState, streamOrderer):
        self.streamOrderer = streamOrderer
        self.sharedState = sharedState

        self.logger =logging.getLogger('nc_node.ncEnqueuer')

    def enqueue(self, cope_packet):
        # Enqueue packet, or send to application layer if
        # final hop
        # Nexthop assignment should probably happen here...
        # based on some routing (Srcr) algorithm?
        # Currently, nexthop addresses are assigned according to previously heard packets, that is learned closest neighbours

        self.logger.debug("Got packet to enqueue")
        self.logger.debug("Encoded NUM %d" % len(cope_packet.encoded_pkts))

        # Control packet
        if len(cope_packet.encoded_pkts) == 0:                                              # TODO: 3.22 us
            # Do not propogate control packets further than overheard hops
            return

        # There should not be multiple encoded packets here
        elif len(cope_packet.encoded_pkts) > 1:                                               # TODO: 2.66 us
            self.logger.critical("Encoded packet lengths in enqueuer should not be longer than 1: %d" % len(cope_packet.encoded_pkts))
            raise Exception("Encoded packet lengths too long")

        # Steps for putting in stream orderer / nexthop queues
        else:
            # Check if I should react to this packet
            if cope_packet.encoded_pkts[0].nexthop_s == self.sharedState.get_my_hw_addr():        # TODO: 6 us
                self.logger.debug("I am the nexthop")

                # Steps for forwarding:
                # If it is a native packet, and I am nexthop, check IP address and forward to neighbour closest

                ip_pkt = cope_packet[ip.IP]

                # Check if the COPE packet contains a IP packet
                if ip_pkt:
                    # 1. Check the encoded IP dest, if it is meant for me, pass it to app layer, and stop forwarding
                    if ip_pkt.dst_s == self.sharedState.get_my_ip_addr():
                        self.logger.debug("The IP packet was meant for me")
                        self.streamOrderer.order_stream(cope_packet)

                    # 2. If not for me, check the final IP dest, and forward to nearest nexthop.
                    # 	If IP address known to us, i.e. closest neighbour known
                    elif ip_pkt.dst_s in self.sharedState.ip_to_mac:  # TODO 5.5 us
                        dst_hw_addr = self.sharedState.getMACFromIP(ip_pkt.dst_s)  # TODO 6.5 us
                        # Update nexthop, so that the next neighbour in the chain will process the packet
                        cope_packet.encoded_pkts[0].nexthop_s = dst_hw_addr  # TODO 12.5 us
                        self.sharedState.times["Enqueuer processed"].append(time.time())
                        self.sharedState.addPacketToOutputQueue(dst_hw_addr, cope_packet)  # TODO 1.7 us
                        # cope_packet.show2()                                                       # TODO 2.7 ms
                    # If IP address is not know, (forward to everyone)
                    else:
                        self.logger.error("IP dest not found in ip_to_mac for ip: %s" % ip_pkt.dst_s)
                        raise Exception("IP dest not found in ip_to_mac for ip: %s" % ip_pkt.dst_s)
                        # self.sharedState.addPacketToOutputQueue(self.broadcast_HWAddr, cope_packet)

            else:
                raise Exception("Packets not meant for me should not arrive at the enquerer")