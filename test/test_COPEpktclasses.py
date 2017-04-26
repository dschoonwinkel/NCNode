import unittest
import COPE_packet_classes as COPE_classes
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('nc_node.test_copepktclasses')
import crc_funcs


class TestCOPEPktClasses(unittest.TestCase):

    def test_COPEpkt_getpktid(self):
        cope_pkt = COPE_classes.COPE_packet()
        hw_dest1 = "00:00:00:00:00:01"
        hw_dest2 = "00:00:00:00:00:02"
        hw_dest3 = "00:00:00:00:00:03"
        header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
        header2 = COPE_classes.EncodedHeader(pkt_id=2, nexthop=hw_dest2)
        header3 = COPE_classes.EncodedHeader(pkt_id=3, nexthop=hw_dest3)

        cope_pkt.encoded_pkts.append(header1)
        cope_pkt.encoded_pkts.append(header2)
        cope_pkt.encoded_pkts.append(header3)

        self.assertEqual(cope_pkt.get_pktid(hw_dest1), 1, "Incorrect pkt_id returned for hw_dest1")
        self.assertEqual(cope_pkt.get_pktid(hw_dest2), 2, "Incorrect pkt_id returned for hw_dest2")
        self.assertEqual(cope_pkt.get_pktid(hw_dest3), 3, "Incorrect pkt_id returned for hw_dest3")

    def test_COPEpkt_calculatechksum(self):
        cope_pkt = COPE_classes.COPE_packet()

        self.assertEqual(cope_pkt.checksum, 0, "Checksum was incorrect before calculations")

        checksum_correct_value = crc_funcs.crc_checksum(str(cope_pkt))
        cope_pkt.calc_checksum()
        self.assertEqual(cope_pkt.checksum, checksum_correct_value, "Checksum was incorrect after calculations")




def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCOPEPktClasses)
    unittest.TextTestRunner(verbosity=2).run(suite)
    logger.debug("Tests run")


if __name__ == '__main__':
    main()
