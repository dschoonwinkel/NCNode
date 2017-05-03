import unittest
import nc_shared_state
import nc_enqueuer
import COPE_packet_classes as COPE_classes
import scapy.all as scapy
import coding_utils
import mock
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('nc_node.test_ncenqueuer')


class TestEnqueuer(unittest.TestCase):

    def test_enqueueControlPacket(self):
        sharedState = nc_shared_state.SharedState()
        mockStreamOrderer = mock.Mock()
        enqueuer = nc_enqueuer.Enqueuer(sharedState, mockStreamOrderer)
        hw_dest1 = "00:00:00:00:00:01"

        cope_pkt1 = COPE_classes.COPE_packet()
        enqueuer.enqueue(cope_pkt1)

        mockStreamOrderer.order_stream.assert_not_called()

    def test_enqueueNativeNotDest(self):
        sharedState = nc_shared_state.SharedState()
        mockStreamOrderer = mock.Mock()
        enqueuer = nc_enqueuer.Enqueuer(sharedState, mockStreamOrderer)
        hw_dest1 = "00:00:00:00:00:01"
        dst_ip = "10.0.0.123"
        # sharedState.ip_to_mac["10.0.0.123"] = hw_dest1

        cope_pkt1 = COPE_classes.COPE_packet() / scapy.IP(dst=dst_ip)
        header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
        payload1 = "\x01"

        cope_pkt1.encoded_pkts.append(header1)
        cope_pkt1.payload = scapy.Raw(payload1)

        enqueuer.enqueue(cope_pkt1)
        mockStreamOrderer.order_stream.assert_not_called()
        enqueued_pkt = sharedState.getPacketFromQueue(hw_dest1)
        enqueued_pkt.show2()
        self.assertEqual(enqueued_pkt, cope_pkt1)


    # def test_decodeNotNexthopEncoded(self):
    #     sharedState = nc_shared_state.SharedState()
    #     mockEnqueuer = mock.Mock()
    #     decoder = nc_decoder.Decoder(sharedState, mockEnqueuer)
    #     hw_dest1 = "00:00:00:00:00:01"
    #     hw_dest2 = "00:00:00:00:00:02"
    #
    #     header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
    #     header2 = COPE_classes.EncodedHeader(pkt_id=2, nexthop=hw_dest2)
    #
    #     payload1 = "\x01"
    #     payload2 = "\x01"
    #
    #     cope_pkt1 = COPE_classes.COPE_packet()
    #
    #     cope_pkt1.encoded_pkts.append(header1)
    #     cope_pkt1.encoded_pkts.append(header2)
    #     cope_pkt1.payload = scapy.Raw("\x00")
    #
    #     cope_pkt2 = COPE_classes.COPE_packet()
    #     cope_pkt2.encoded_pkts.append(header2)
    #     cope_pkt2.payload = scapy.Raw(payload2)
    #
    #     sharedState.addPacketToPacketPool(2, cope_pkt2)
    #
    #     decoder.decode(cope_pkt1, hw_dest1)
    #
    #     mockEnqueuer.enqueue.assert_not_called()
    #     self.assertFalse(sharedState.wasPktIdReceived(1))
    #
    # def test_decodeNexthopNative(self):
    #     sharedState = nc_shared_state.SharedState()
    #     mockEnqueuer = mock.Mock()
    #     decoder = nc_decoder.Decoder(sharedState, mockEnqueuer)
    #     hw_dest1 = sharedState.get_my_hw_addr()
    #     header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
    #     payload1 = "\x01"
    #
    #     cope_pkt1 = COPE_classes.COPE_packet()
    #
    #     cope_pkt1.encoded_pkts.append(header1)
    #     cope_pkt1.payload = scapy.Raw(payload1)
    #
    #     result = decoder.decode(cope_pkt1, hw_dest1)
    #
    #     self.assertTrue(sharedState.wasPktIdReceived(1))
    #     mockEnqueuer.enqueue.assert_called_with(cope_pkt1)
    #
    # def test_decodeNexthopEncoded(self):
    #     sharedState = nc_shared_state.SharedState()
    #     mockEnqueuer = mock.Mock()
    #     decoder = nc_decoder.Decoder(sharedState, mockEnqueuer)
    #     hw_dest1 = sharedState.get_my_hw_addr()
    #     hw_dest2 = "00:00:00:00:00:02"
    #
    #     header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
    #     header2 = COPE_classes.EncodedHeader(pkt_id=2, nexthop=hw_dest2)
    #
    #     payload1 = "\x01"
    #     payload2 = "\x01"
    #
    #     cope_pkt1 = COPE_classes.COPE_packet()
    #
    #     cope_pkt1.encoded_pkts.append(header1)
    #     cope_pkt1.encoded_pkts.append(header2)
    #     cope_pkt1.payload = scapy.Raw("\x00")
    #
    #     cope_pkt2 = COPE_classes.COPE_packet()
    #     cope_pkt2.encoded_pkts.append(header2)
    #     cope_pkt2.payload = scapy.Raw(payload2)
    #
    #     sharedState.addPacketToPacketPool(2, cope_pkt2)
    #
    #     decoder.decode(cope_pkt1, hw_dest1)
    #
    #     # mockEnqueuer.enqueue.assert_called()
    #     # mockEnqueuer.enqueue.assert_called_with(cope_pkt1)

def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnqueuer)
    unittest.TextTestRunner(verbosity=2).run(suite)
    logger.debug("Tests run")

if __name__ == '__main__':
    main()