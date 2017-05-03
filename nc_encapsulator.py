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
        self.broadcast_HWAddr = "ff:ff:ff:ff:ff:ff"

    def encapsulate(self, data, IP_addr):
        self.logger.debug("Got packet to encapsulate")

        src_ip = self.sharedState.get_my_ip_addr()
        local_seq_no = self.sharedState.getAndIncrementLocalSeqNum()
        pkt_id = COPE_classes.generatePktId(src_ip, local_seq_no)

        ip_pkt = scapy.IP(src=src_ip, dst=IP_addr) / scapy.UDP(dport=14541) / scapy.Raw(data)
        cope_pkt = COPE_classes.COPE_packet() / ip_pkt

        # Use broadcast address as "empty" addr field
        cope_pkt.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id, nexthop=self.broadcast_HWAddr))
        cope_pkt.local_pkt_seq_num = local_seq_no

        # self.logger.debug(coding_utils.print_hex("IP packet hex", str(ip_pkt)))
        # cope_pkt.show2()
        self.enqueuer.enqueue(cope_pkt)