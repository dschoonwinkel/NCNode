import logging
logging.basicConfig(level=logging.DEBUG)
import logging.config
import crc_funcs
from pypacker.layer12 import cope, ethernet
import time
logging.config.fileConfig('logging.conf')

class Transmitter(object):

    def __init__(self, sharedState):
        self.sharedState = sharedState
        self.broadcast_HWAddr = "ff:ff:ff:ff:ff:ff"

        self.logger =logging.getLogger('nc_node.Transmitter')

    def transmit(self, pkt):
        networkInstance = self.sharedState.getNetworkInstance()

        # pkt.show2()

        if networkInstance:
            #self.#logger.debug("Transmitting packet\n")

            # Calculate final checksum here
            # pkt.calc_checksum()
            encap_pkt = None
            # #logger.debug(Encoded num", pkt.ENCODED_NUM

            # Do packet encapsulation here...
            # #self.#logger.debug("my hw addr: %s" % self.sharedState.get_my_hw_addr())

            if len(pkt.encoded_pkts) == 0:
                encap_pkt = ethernet.Ethernet(src_s=self.sharedState.get_my_hw_addr(), dst_s=self.broadcast_HWAddr, type=cope.COPE_PACKET_TYPE)+pkt
            elif len(pkt.encoded_pkts) == 1:
                encap_pkt = ethernet.Ethernet(src_s=self.sharedState.get_my_hw_addr(), dst_s=pkt.encoded_pkts[0].nexthop_s, type=cope.COPE_PACKET_TYPE)+pkt
                # self.logger.debug(str(encap_pkt))
                # self.logger.debug(encap_pkt.bin())
                self.sharedState.incrementPktsSent(encoded = False)

            elif len(pkt.encoded_pkts) > 1:
                encap_pkt = ethernet.Ethernet(src_s=self.sharedState.get_my_hw_addr(), dst_s=self.broadcast_HWAddr, type=cope.COPE_PACKET_TYPE)+pkt
                self.sharedState.incrementPktsSent(encoded = True)
            else:
                self.logger.error("Impossible ENCODED_NUM, stopping transmit")
                return

            # encap_pkt.show2()

            self.sharedState.resetControlPktScheduler()
            self.sharedState.times["Transmitter send"].append(time.time())
            networkInstance.sendPkt(encap_pkt)

        else:
            #self.#logger.debug("Network Instance was null, not transmitting\n")
            pass

    def dropPkt(self, pkt_id):
        networkInstance = self.sharedState.getNetworkInstance()

        if networkInstance:
            #self.#logger.debug("Dropping packet %d", pkt_id)
            networkInstance.dropPkt(pkt_id)