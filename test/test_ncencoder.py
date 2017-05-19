import unittest
import nc_shared_state
import nc_encoder
import COPE_packet_classes as COPE_classes
import scapy.all as scapy
import coding_utils
import mock
import logging
import logging.config
logging.config.fileConfig('logging.conf')
#logger =logging.getLogger('nc_node.test_ncencoder')


class TestEncoder(unittest.TestCase):

    def test_encode(self):
        sharedState = nc_shared_state.SharedState()
        mockAddAcksRecps = mock.Mock()
        encoder = nc_encoder.Encoder(sharedState, mockAddAcksRecps)
        hw_dest1 = "00:00:00:00:00:01"
        hw_dest2 = "00:00:00:00:00:02"
        hw_dest3 = "00:00:00:00:00:03"
        header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
        header2 = COPE_classes.EncodedHeader(pkt_id=2, nexthop=hw_dest2)
        header3 = COPE_classes.EncodedHeader(pkt_id=3, nexthop=hw_dest3)
        payload1 = "\x01"
        payload2 = "\x02"
        payload3 = "\x04"

        cope_pkt1 = COPE_classes.COPE_packet()

        cope_pkt1.encoded_pkts.append(header1)
        cope_pkt1.payload = scapy.Raw(payload1)

        cope_pkt2 = COPE_classes.COPE_packet()

        cope_pkt2.encoded_pkts.append(header2)
        cope_pkt2.payload = scapy.Raw(payload2)

        cope_pkt3 = COPE_classes.COPE_packet()

        cope_pkt3.encoded_pkts.append(header3)
        cope_pkt3.payload = scapy.Raw(payload3)

        sharedState.addPacketToOutputQueue(hw_dest2, cope_pkt2)
        sharedState.addPacketToOutputQueue(hw_dest3, cope_pkt3)

        # Set up neighbours so that they have already received other neighbour's missing packets
        sharedState.neighbour_recvd[hw_dest1] = set()
        sharedState.neighbour_recvd[hw_dest1].add(2)
        sharedState.neighbour_recvd[hw_dest1].add(3)

        sharedState.neighbour_recvd[hw_dest2] = set()
        sharedState.neighbour_recvd[hw_dest2].add(1)
        sharedState.neighbour_recvd[hw_dest2].add(3)

        sharedState.neighbour_recvd[hw_dest3] = set()
        sharedState.neighbour_recvd[hw_dest3].add(1)
        sharedState.neighbour_recvd[hw_dest3].add(2)

        encoder.encode(cope_pkt1)

        mockAddAcksRecps.addACKsRecps.assert_called()
        encoded_pkt = mockAddAcksRecps.addACKsRecps.call_args_list[0][0][0]
        self.assertEqual(str(encoded_pkt.payload), "\x07", "Encoding failed")

        # header1.show2()
        # encoded_pkt.encoded_pkts[0].show2()
        # print encoded_pkt.encoded_pkts
        # encoded_pkt.show2()

        encoded_headers = encoded_pkt.encoded_pkts
        self.assertTrue(header1 in encoded_headers, "Header 1 was not in encoded_headers")
        self.assertTrue(header2 in encoded_headers, "Header 2 was not in encoded_headers")
        self.assertTrue(header3 in encoded_headers, "Header 3 was not in encoded_headers")

        # self.assertEqual(str(encoded_pkt.encoded_pkts[0]), str(header1), "Encoded header 1 incorrect")
        # self.assertEqual(str(encoded_pkt.encoded_pkts[2]), str(header2), "Encoded header 2 incorrect")
        # self.assertEqual(str(encoded_pkt.encoded_pkts[1]), str(header3), "Encoded header 3 incorrect")

    def test_encode_native(self):
        sharedState = nc_shared_state.SharedState()
        mockAddAcksRecps = mock.Mock()
        encoder = nc_encoder.Encoder(sharedState, mockAddAcksRecps)
        hw_dest1 = "00:00:00:00:00:01"
        header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
        payload1 = "\x01"

        cope_pkt1 = COPE_classes.COPE_packet()

        cope_pkt1.encoded_pkts.append(header1)
        cope_pkt1.payload = scapy.Raw(payload1)

        encoder.encode(cope_pkt1)

        mockAddAcksRecps.addACKsRecps.assert_called()
        encoded_pkt = mockAddAcksRecps.addACKsRecps.call_args_list[0][0][0]

        # ENCODED_NUM is not calculated correctly if the packet is not sent on the wire
        # self.assertEqual(encoded_pkt.ENCODED_NUM, 1, "ENCODED_NUM incorrect")
        self.assertEqual(len(encoded_pkt.encoded_pkts), 1, "Encoded headers wrong len")

        self.assertEqual(str(encoded_pkt.payload), "\x01", "Encoding failed")

        self.assertEqual(str(encoded_pkt.encoded_pkts[0]), str(header1), "Encoded header 1 incorrect")


    def test_findcodables(self):
        sharedState = nc_shared_state.SharedState()
        mockAddAcksRecps = mock.Mock()
        encoder = nc_encoder.Encoder(sharedState, mockAddAcksRecps)

        # Create three different packets, meant for 3 destinations. Packets can only be coded together if each
        # neighbour can decode their respective packets
        hw_dest1 = "00:00:00:00:00:01"
        hw_dest2 = "00:00:00:00:00:02"
        hw_dest3 = "00:00:00:00:00:03"
        header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
        cope_pkt1 = COPE_classes.COPE_packet()
        cope_pkt1.encoded_pkts.append(header1)

        header2 = COPE_classes.EncodedHeader(pkt_id=2, nexthop=hw_dest2)
        cope_pkt2 = COPE_classes.COPE_packet()
        cope_pkt2.encoded_pkts.append(header2)

        header3 = COPE_classes.EncodedHeader(pkt_id=3, nexthop=hw_dest3)
        cope_pkt3 = COPE_classes.COPE_packet()
        cope_pkt3.encoded_pkts.append(header3)


        # Set up neighbours so that they have already received other neighbour's missing packets
        sharedState.neighbour_recvd[hw_dest1] = set()
        sharedState.neighbour_recvd[hw_dest1].add(2)
        sharedState.neighbour_recvd[hw_dest1].add(3)

        sharedState.neighbour_recvd[hw_dest2] = set()
        sharedState.neighbour_recvd[hw_dest2].add(1)
        sharedState.neighbour_recvd[hw_dest2].add(3)

        sharedState.neighbour_recvd[hw_dest3] = set()
        sharedState.neighbour_recvd[hw_dest3].add(1)
        sharedState.neighbour_recvd[hw_dest3].add(2)

        cope_pkt_list = list([cope_pkt1, cope_pkt2, cope_pkt3])

        valid_pkts, rest_pkts = encoder.findCodables(cope_pkt_list)

        self.assertTrue(cope_pkt1 in valid_pkts, "Packet1 was not in valid packets")
        self.assertTrue(cope_pkt2 in valid_pkts, "Packet1 was not in valid packets")
        self.assertTrue(cope_pkt3 in valid_pkts, "Packet1 was not in valid packets")

    def test_findcodables_missing1(self):
        sharedState = nc_shared_state.SharedState()
        mockAddAcksRecps = mock.Mock()
        encoder = nc_encoder.Encoder(sharedState, mockAddAcksRecps)

        # Create three different packets, meant for 3 destinations. Packets can only be coded together if each
        # neighbour can decode their respective packets
        hw_dest1 = "00:00:00:00:00:01"
        hw_dest2 = "00:00:00:00:00:02"
        hw_dest3 = "00:00:00:00:00:03"
        header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
        cope_pkt1 = COPE_classes.COPE_packet()
        cope_pkt1.encoded_pkts.append(header1)

        header2 = COPE_classes.EncodedHeader(pkt_id=2, nexthop=hw_dest2)
        cope_pkt2 = COPE_classes.COPE_packet()
        cope_pkt2.encoded_pkts.append(header2)

        header3 = COPE_classes.EncodedHeader(pkt_id=3, nexthop=hw_dest3)
        cope_pkt3 = COPE_classes.COPE_packet()
        cope_pkt3.encoded_pkts.append(header3)

        # Set up neighbours so that they have already received other neighbour's missing packets
        sharedState.neighbour_recvd[hw_dest1] = set()
        sharedState.neighbour_recvd[hw_dest1].add(2)

        sharedState.neighbour_recvd[hw_dest2] = set()
        sharedState.neighbour_recvd[hw_dest2].add(1)
        sharedState.neighbour_recvd[hw_dest2].add(3)

        sharedState.neighbour_recvd[hw_dest3] = set()
        sharedState.neighbour_recvd[hw_dest3].add(1)
        sharedState.neighbour_recvd[hw_dest3].add(2)

        cope_pkt_list = list([cope_pkt1, cope_pkt2, cope_pkt3])

        valid_pkts, rest_pkts = encoder.findCodables(cope_pkt_list)

        self.assertTrue(cope_pkt1 in valid_pkts, "Packet1 was not in valid packets")
        self.assertTrue(cope_pkt2 in valid_pkts, "Packet2 was not in valid packets")
        self.assertTrue(cope_pkt3 not in valid_pkts, "Packet3 not in valid packets")

    def test_findcodables_missing2(self):
        sharedState = nc_shared_state.SharedState()
        mockAddAcksRecps = mock.Mock()
        encoder = nc_encoder.Encoder(sharedState, mockAddAcksRecps)

        # Create three different packets, meant for 3 destinations. Packets can only be coded together if each
        # neighbour can decode their respective packets
        hw_dest1 = "00:00:00:00:00:01"
        hw_dest2 = "00:00:00:00:00:02"
        hw_dest3 = "00:00:00:00:00:03"
        header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
        cope_pkt1 = COPE_classes.COPE_packet()
        cope_pkt1.encoded_pkts.append(header1)

        header2 = COPE_classes.EncodedHeader(pkt_id=2, nexthop=hw_dest2)
        cope_pkt2 = COPE_classes.COPE_packet()
        cope_pkt2.encoded_pkts.append(header2)

        header3 = COPE_classes.EncodedHeader(pkt_id=3, nexthop=hw_dest3)
        cope_pkt3 = COPE_classes.COPE_packet()
        cope_pkt3.encoded_pkts.append(header3)


        # Set up neighbours so that they have already received other neighbour's missing packets
        sharedState.neighbour_recvd[hw_dest1] = set()

        sharedState.neighbour_recvd[hw_dest2] = set()
        sharedState.neighbour_recvd[hw_dest2].add(1)
        sharedState.neighbour_recvd[hw_dest2].add(3)

        sharedState.neighbour_recvd[hw_dest3] = set()
        sharedState.neighbour_recvd[hw_dest3].add(1)
        sharedState.neighbour_recvd[hw_dest3].add(2)

        cope_pkt_list = list([cope_pkt1, cope_pkt2, cope_pkt3])

        valid_pkts, rest_pkts = encoder.findCodables(cope_pkt_list)

        self.assertTrue(cope_pkt1 in valid_pkts, "Packet1 was not in valid packets")
        self.assertTrue(cope_pkt2 not in valid_pkts, "Packet2 was in valid packets")
        self.assertTrue(cope_pkt3 not in valid_pkts, "Packet3 was in valid packets")

    def test_findcodables_missing3(self):
        sharedState = nc_shared_state.SharedState()
        mockAddAcksRecps = mock.Mock()
        encoder = nc_encoder.Encoder(sharedState, mockAddAcksRecps)

        # Create three different packets, meant for 3 destinations. Packets can only be coded together if each
        # neighbour can decode their respective packets
        hw_dest1 = "00:00:00:00:00:01"
        hw_dest2 = "00:00:00:00:00:02"
        hw_dest3 = "00:00:00:00:00:03"
        header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
        cope_pkt1 = COPE_classes.COPE_packet()
        cope_pkt1.encoded_pkts.append(header1)

        header2 = COPE_classes.EncodedHeader(pkt_id=2, nexthop=hw_dest2)
        cope_pkt2 = COPE_classes.COPE_packet()
        cope_pkt2.encoded_pkts.append(header2)

        header3 = COPE_classes.EncodedHeader(pkt_id=3, nexthop=hw_dest3)
        cope_pkt3 = COPE_classes.COPE_packet()
        cope_pkt3.encoded_pkts.append(header3)


        # Set up neighbours so that they have already received other neighbour's missing packets
        sharedState.neighbour_recvd[hw_dest1] = set()

        sharedState.neighbour_recvd[hw_dest2] = set()
        sharedState.neighbour_recvd[hw_dest2].add(3)

        sharedState.neighbour_recvd[hw_dest3] = set()
        sharedState.neighbour_recvd[hw_dest3].add(1)
        sharedState.neighbour_recvd[hw_dest3].add(2)

        cope_pkt_list = list([cope_pkt1, cope_pkt2, cope_pkt3])

        valid_pkts, rest_pkts = encoder.findCodables(cope_pkt_list)

        self.assertTrue(cope_pkt1 not in valid_pkts, "Packet1 was in valid packets")
        self.assertTrue(cope_pkt2 not in valid_pkts, "Packet2 was in valid packets")
        self.assertTrue(cope_pkt3 not in valid_pkts, "Packet3 was in valid packets")

def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEncoder)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #logger.debug("Tests run")

if __name__ == '__main__':
    main()