import unittest
import nc_shared_state
import nc_decoder
import COPE_packet_classes as COPE_classes
import scapy.all as scapy
import coding_utils
import mock
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('nc_node.test_ncencoder')


class TestEncoder(unittest.TestCase):

    def test_decodeControlPacket(self):
        sharedState = nc_shared_state.SharedState()
        mockEnqueuer = mock.Mock()
        decoder = nc_decoder.Decoder(sharedState, mockEnqueuer)
        hw_dest1 = "00:00:00:00:00:01"

        cope_pkt1 = COPE_classes.COPE_packet()

        self.assertTrue(decoder.decode(cope_pkt1, hw_dest1), "Control packet decode did not return True")
        # Enqueuer should not be called for control packets, that is packets with only network state updates
        mockEnqueuer.enqueue.assert_not_called()

    def test_decodeNotNexthopNative(self):
        sharedState = nc_shared_state.SharedState()
        mockEnqueuer = mock.Mock()
        decoder = nc_decoder.Decoder(sharedState, mockEnqueuer)
        hw_dest1 = "00:00:00:00:00:01"
        header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
        payload1 = "\x01"

        cope_pkt1 = COPE_classes.COPE_packet()

        cope_pkt1.encoded_pkts.append(header1)
        cope_pkt1.payload = scapy.Raw(payload1)

        result = decoder.decode(cope_pkt1, hw_dest1)

        self.assertTrue(sharedState.wasPktIdReceived(1))


    def test_decodeNotNexthopEncoded(self):
        sharedState = nc_shared_state.SharedState()
        mockEnqueuer = mock.Mock()
        decoder = nc_decoder.Decoder(sharedState, mockEnqueuer)
        hw_dest1 = "00:00:00:00:00:01"
        hw_dest2 = "00:00:00:00:00:02"

        header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
        header2 = COPE_classes.EncodedHeader(pkt_id=2, nexthop=hw_dest2)

        payload1 = "\x01"
        payload2 = "\x01"

        cope_pkt1 = COPE_classes.COPE_packet()

        cope_pkt1.encoded_pkts.append(header1)
        cope_pkt1.encoded_pkts.append(header2)
        cope_pkt1.payload = scapy.Raw("\x00")

        cope_pkt2 = COPE_classes.COPE_packet()
        cope_pkt2.encoded_pkts.append(header2)
        cope_pkt2.payload = scapy.Raw(payload2)

        sharedState.addPacketToPacketPool(2, cope_pkt2)

        decoder.decode(cope_pkt1, hw_dest1)

        mockEnqueuer.enqueue.assert_not_called()
        self.assertFalse(sharedState.wasPktIdReceived(1))

    def test_decodeNexthopNative(self):
        sharedState = nc_shared_state.SharedState()
        mockEnqueuer = mock.Mock()
        decoder = nc_decoder.Decoder(sharedState, mockEnqueuer)
        hw_dest1 = sharedState.get_my_hw_addr()
        header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
        payload1 = "\x01"

        cope_pkt1 = COPE_classes.COPE_packet()

        cope_pkt1.encoded_pkts.append(header1)
        cope_pkt1.payload = scapy.Raw(payload1)

        result = decoder.decode(cope_pkt1, hw_dest1)

        self.assertTrue(sharedState.wasPktIdReceived(1))
        mockEnqueuer.enqueue.assert_called_with(cope_pkt1)

    def test_decodeNexthopEncoded(self):
        sharedState = nc_shared_state.SharedState()
        mockEnqueuer = mock.Mock()
        decoder = nc_decoder.Decoder(sharedState, mockEnqueuer)
        hw_dest1 = sharedState.get_my_hw_addr()
        hw_dest2 = "00:00:00:00:00:02"

        header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)
        header2 = COPE_classes.EncodedHeader(pkt_id=2, nexthop=hw_dest2)

        payload1 = "\x01"
        payload2 = "\x01"

        cope_pkt1 = COPE_classes.COPE_packet()

        cope_pkt1.encoded_pkts.append(header1)
        cope_pkt1.encoded_pkts.append(header2)
        cope_pkt1.payload = scapy.Raw("\x00")

        cope_pkt2 = COPE_classes.COPE_packet()
        cope_pkt2.encoded_pkts.append(header2)
        cope_pkt2.payload = scapy.Raw(payload2)

        sharedState.addPacketToPacketPool(2, cope_pkt2)

        decoder.decode(cope_pkt1, hw_dest1)

        # mockEnqueuer.enqueue.assert_called()
        # mockEnqueuer.enqueue.assert_called_with(cope_pkt1)

def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEncoder)
    unittest.TextTestRunner(verbosity=2).run(suite)
    logger.debug("Tests run")

if __name__ == '__main__':
    main()