import unittest
import nc_shared_state
import nc_enqueuer
import coding_utils
from unittest.mock import Mock
import logging
from pypacker.layer12 import cope
from pypacker.layer3 import ip
import logging.config
logging.config.fileConfig('logging.conf')
#logger =logging.getLogger('nc_node.test_ncenqueuer')


class TestEnqueuer(unittest.TestCase):

    def test_enqueueControlPacket(self):
        sharedState = nc_shared_state.SharedState()
        mockStreamOrderer = Mock()
        enqueuer = nc_enqueuer.Enqueuer(sharedState, mockStreamOrderer)
        hw_dest1 = "00:00:00:00:00:01"

        cope_pkt1 = cope.COPE_packet()
        enqueuer.enqueue(cope_pkt1)

        mockStreamOrderer.order_stream.assert_not_called()

    def test_enqueueNativeNotDest(self):
        sharedState = nc_shared_state.SharedState()
        mockStreamOrderer = Mock()
        enqueuer = nc_enqueuer.Enqueuer(sharedState, mockStreamOrderer)
        hw_dest1 = "00:00:00:00:00:23"
        dst_ip = "10.0.0.123"
        sharedState.ip_to_mac["10.0.0.123"] = hw_dest1
        payload1 = b"\x01"

        cope_pkt1 = cope.COPE_packet()
        header1 = cope.EncodedHeader(pkt_id=1, nexthop_s=hw_dest1)
        cope_pkt1.encoded_pkts.append(header1)
        encap_packet = cope_pkt1 + ip.IP(dst_s=dst_ip)
        encap_packet[ip.IP].body_bytes = payload1

        enqueuer.enqueue(encap_packet)
        mockStreamOrderer.order_stream.assert_not_called()
        # print("Shared state packet queues", sharedState.packet_queues.keys())

        enqueued_pkt = sharedState.getPacketFromQueue(hw_dest1)
        self.assertEqual(enqueued_pkt, encap_packet)

def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEnqueuer)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #logger.debug("Tests run")

if __name__ == '__main__':
    main()