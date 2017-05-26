import scapy.all as scapy
import logging
import logging.config
import COPE_packet_classes as COPE_classes
import time

class Encapsulator(object):

    def __init__(self, sharedState, enqueuer):
        self.sharedState = sharedState
        self.enqueuer = enqueuer
        logging.config.fileConfig('logging.conf')
        #self.#logger =logging.getLogger('nc_node.Encapsulator')
        self.broadcast_HWAddr = "ff:ff:ff:ff:ff:ff"

    def encapsulate(self, data, IP_addr):
        #self.#logger.debug("Got packet to encapsulate")

        src_ip = self.sharedState.get_my_ip_addr()                                          # TODO 303 ns
        local_seq_no = self.sharedState.getAndIncrementLocalSeqNum()                        # TODO 422 ns
        pkt_id = COPE_classes.generatePktId(src_ip, local_seq_no)                           # TODO 10 us

        ip_pkt = scapy.IP(src=src_ip, dst=IP_addr, id=local_seq_no) / scapy.UDP(sport=11777, dport=14541) / scapy.Raw(data) # TODO 1.2 ms
        cope_pkt = COPE_classes.COPE_packet() / ip_pkt                                      # TODO 750 us

        # Use broadcast address as "empty" addr field
        #cope_pkt.encoded_pkts = list()                                                      # TODO 14 us
        cope_pkt.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id, nexthop=self.broadcast_HWAddr))  # TODO 66 us
        cope_pkt.local_pkt_seq_num = local_seq_no           # TODO 4.91 us per loop

        # cope_pkt.show2()

        self.sharedState.times["Encapsulator processed"].append(time.time())                # TODO 613 ns


        self.enqueuer.enqueue(cope_pkt)