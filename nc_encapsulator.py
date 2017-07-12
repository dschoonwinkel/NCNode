from pypacker.layer12.cope import COPE_packet, EncodedHeader
from pypacker.layer3.ip import IP
from pypacker.layer4.udp import UDP
import logging
import logging.config
# import COPE_packet_classes as COPE_classes
import time

logging.config.fileConfig('logging.conf')

class Encapsulator(object):

    def __init__(self, sharedState, enqueuer):
        self.sharedState = sharedState
        self.enqueuer = enqueuer

        #self.#logger =logging.getLogger('nc_node.Encapsulator')
        self.broadcast_HWAddr = "ff:ff:ff:ff:ff:ff"

    def encapsulate(self, data, IP_addr):
        #self.#logger.debug("Got packet to encapsulate")

        src_ip = self.sharedState.get_my_ip_addr()                                          # TODO 303 ns
        local_seq_no = self.sharedState.getAndIncrementLocalSeqNum()                        # TODO 422 ns
        pkt_id = COPE_packet.generatePktId(src_ip, local_seq_no)                           # TODO 3 us

        cope_pkt = COPE_packet() + IP(src_s=src_ip, dst_s=IP_addr, id=local_seq_no) + UDP(sport=11777, dport=14541)  # TODO 90 us
        if type(data) == str:
            data = data.encode('utf-8')
        cope_pkt[UDP].body_bytes = data

        # Use broadcast address as "empty" addr field
        #cope_pkt.encoded_pkts = list()                                                      # TODO 14 us
        cope_pkt.encoded_pkts.append(EncodedHeader(pkt_id=pkt_id, nexthop_s=self.broadcast_HWAddr))
        cope_pkt.local_pkt_seq_num = local_seq_no           # TODO 4.91 us per loop

        self.sharedState.times["Encapsulator processed"].append(time.time())                # TODO 613 ns


        self.enqueuer.enqueue(cope_pkt)