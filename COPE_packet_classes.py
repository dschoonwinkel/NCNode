from scapy.all import *
import crc_funcs

COPE_PACKET_TYPE = 0x7123

class EncodedHeader(Packet):
    name = "Encoded packets"

    fields_desc = [LongField('pkt_id', 0),
                   MACField('nexthop', "00:00:00:00:00:00")]

    def extract_padding(self, s):
      return '',s

class ReportHeader(Packet):
    name = "Overheard report"

    fields_desc = [IPField('src_ip', "0.0.0.0"), 
                   LongField('last_pkt', 0),
                   ByteField('bit_map', '0')]

    def extract_padding(self, s):
      return '',s

class ACKHeader(Packet):
    name = "ACK report"

    fields_desc = [MACField('neighbour', "00:00:00:00:00:00"), 
                   LongField('last_ack', 0),
                   ByteField('ack_map', 0)]

    def extract_padding(self, s):
      return '',s

class COPE_packet(Packet):
    name = "COPE packet"
    fields_desc = [FieldLenField("ENCODED_NUM", None, count_of='encoded_pkts'),
            PacketListField('encoded_pkts', None, EncodedHeader, 
                                   count_from = lambda pkt: pkt.ENCODED_NUM),
            FieldLenField("REPORT_NUM", None, count_of='reports'),
            PacketListField('reports', None, ReportHeader, 
                                   count_from = lambda pkt: pkt.REPORT_NUM),
            FieldLenField("ACK_NUM", None, count_of='acks'),
            IntField("local_pkt_seq_num", 0),
            PacketListField('acks', None, ACKHeader, 
                                   count_from = lambda pkt: pkt.ACK_NUM),
            ShortField("checksum", 0)]

    def calc_checksum(self):
      # Remember to calculate checksum only of COPE header and not the whole packet
      payload_len = len(self.payload)
      if payload_len != 0:
        self.checksum = crc_funcs.crc_checksum(str(self)[:-payload_len])
      else:
        self.checksum = crc_funcs.crc_checksum(str(self))

    def get_pktid(self, neighbour):
        for encoded_header in self.encoded_pkts:
            if encoded_header.nexthop == neighbour:
                return encoded_header.pkt_id

    def check_nexthops(self, neighbour):
        # Check if neighbour is addressed in this packet's nexthops
        for encoded_header in self.encoded_pkts:
            if encoded_header.nexthop == neighbour:
                return True

        return False

    @staticmethod
    def generatePktId(src_ip, pkt_seq_no):
        pkt_id_str = src_ip + str(pkt_seq_no)
        pkt_id = crc_funcs.crc_hash(pkt_id_str)

        return pkt_id


def main():
  cope_pkt = COPE_packet()
  cope_pkt.encoded_pkts.append(EncodedHeader(pkt_id=hash("10.0.0.1"+str(1)), nexthop="00:00:00:10:00:02"))
  cope_pkt.local_pkt_seq_num = 1
  cope_pkt.show2()
  ls(cope_pkt)
  hextext = ' '.join('%02X' % ord(x) for x in str(cope_pkt))
  print hextext


if __name__ == '__main__':
  main()