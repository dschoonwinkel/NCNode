import unittest
import nc_shared_state
import nc_encapsulator
import scapy.all as scapy
import COPE_packet_classes as COPE_classes
import coding_utils
from unittest.mock import Mock
import logging
import logging.config
logging.config.fileConfig('logging.conf')
import pypacker.layer12
#logger =logging.getLogger('nc_node.test_ncenqueuer')


class TestEncapsulator(unittest.TestCase):

    def test_encapsulate(self):
        sharedState = nc_shared_state.SharedState()
        mockEnqueuer = Mock()
        encapsulator = nc_encapsulator.Encapsulator(sharedState, mockEnqueuer)
        hw_dest1 = "00:00:00:00:00:01"
        broadcast_HWAddr = "ff:ff:ff:ff:ff:ff"
        data = "Hello World!"
        IP_addr = "10.0.0.3"

        src_ip = sharedState.get_my_ip_addr()
        local_seq_no = sharedState.getAndIncrementLocalSeqNum()
        # print(local_seq_no)
        sharedState.local_ip_seq_num -= 1
        pkt_id = COPE_classes.generatePktId(src_ip, local_seq_no)

        # Old way of doing things, results in byte string below, using scapy
        #
        pkt = COPE_classes.COPE_packet() / scapy.IP(src=src_ip, dst=IP_addr, id=local_seq_no) / scapy.UDP(sport=11777, dport=14541) / data
        pkt.encoded_pkts.append(
            COPE_classes.EncodedHeader(pkt_id=pkt_id, nexthop=broadcast_HWAddr))  # TODO 66 us
        pkt.local_pkt_seq_num = local_seq_no

        pkt.calc_checksum()
        # # byte_string = b'\x00\x01&W\xe9\x8e\x0e^\r>\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x01\xb8nE\x00\x00(\x00\x01\x00\x00@\x11d\xb3\n\x00\x02\x0f\n\x00\x00\x03.\x018\xcd\x00\x140\xf7Hello World!'
        # byte_string = b'\x00\x01\x11)\x8e\r>\r>\r\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x8bE\x00\x00(\x00\x01\x00\x00@\x11f\xc1\n\x00\x00\x01\n\x00\x00\x03.\x018\xcd\x00\x143\x05Hello World!'

        # byte_string2 = b'\x00\x01&W\xe9\x8e\x0e^\r>\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00E\x00\x00(\x00\x01\x00\x00@\x11f\xc1\n\x00\x00\x01\n\x00\x00\x03.\x018\xcd\x00\x143\x05Hello World!'

        byte_string = pkt.build()
        encapsulator.encapsulate(data, IP_addr)

        mockEnqueuer.enqueue.assert_called()
        sent_pkt = mockEnqueuer.enqueue.call_args_list[0][0][0]

        # print(pypacker.layer12.COPE_packet.COPE_packet(byte_string))

        # print("\n1\n", byte_string)
        # print("2", sent_pkt.bin())

        # print(coding_utils.print_hex("Byte string", byte_string))
        # print(coding_utils.print_hex("Sent packet", sent_pkt.bin()))
        # print(sent_pkt.bin())

        # print(sent_pkt)
        # print(coding_utils.bytexor(byte_string, sent_pkt.bin())[20:28])

        self.assertEqual(byte_string, sent_pkt.bin())



def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEncapsulator)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #logger.debug("Tests run")

if __name__ == '__main__':
    main()