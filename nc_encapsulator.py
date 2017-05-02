import scapy.all as scapy
import logging
import logging.config
import COPE_packet_classes as COPE_classes
import coding_utils

class Encapsulator(object):

    def __init__(self, sharedState, enqueuer):
        self.sharedState = sharedState
        self.enqueuer = enqueuer
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('nc_node.Encapsulator')

    def encapsulate(self, data, IP_addr):
        self.logger.debug("Got packet to encapsulate")

        ip_pkt = scapy.IP(src=self.sharedState.get_my_ip_addr(), dst=IP_addr) / scapy.UDP(dport=14541) / scapy.Raw(data)
        cope_pkt = COPE_classes.COPE_packet() / ip_pkt

        # self.logger.debug(coding_utils.print_hex("IP packet hex", str(ip_pkt)))
        # cope_pkt.show2()

        self.enqueuer.enqueue(cope_pkt)