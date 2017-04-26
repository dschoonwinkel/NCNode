import unittest
import nc_shared_state
import COPE_packet_classes as COPE_classes
import scapy.all as scapy
import coding_utils
import nc_acks_receipts
import mock
import time
import nc_acks_receipts
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('nc_node.test_ncacksreceipt')


class TestACKRecps(unittest.TestCase):
    def test_processPkt_ack(self):
        mockDecoder = mock.Mock()
        sharedState = nc_shared_state.SharedState()
        acksRecps = nc_acks_receipts.ACKsReceipts(sharedState, mockDecoder)
        src_HWAddr = sharedState.get_my_hw_addr()
        neighbourMAC = "000:00:00:00:00:02"

        # Set up ACKWaiters
        mockACKWaiter_pkt10 = mock.Mock()
        mockACKWaiter_pkt2 = mock.Mock()
        mockACKWaiter_pkt3 = mock.Mock()

        sharedState.addACK_waiter(neighbourMAC, 10, mockACKWaiter_pkt10)
        sharedState.addACK_waiter(neighbourMAC, 3, mockACKWaiter_pkt3)
        sharedState.addACK_waiter(neighbourMAC, 2, mockACKWaiter_pkt2)

        ackcope_pkt = COPE_classes.COPE_packet()

        # ACKs packet 10, as well as (1100 0000), i.e. packets 2,3
        ackHeader = COPE_classes.ACKHeader(neighbour=src_HWAddr, last_ack=10, ack_map=192)
        ackcope_pkt.acks.append(ackHeader)
        acksRecps.processPkt(ackcope_pkt, neighbourMAC)

        mockACKWaiter_pkt10.stopWaiter.assert_called()
        mockACKWaiter_pkt3.stopWaiter.assert_called()
        mockACKWaiter_pkt2.stopWaiter.assert_called()

        mockDecoder.decode.assert_called()

    def test_processPkt_recp(self):
        mockDecoder = mock.Mock()
        sharedState = nc_shared_state.SharedState()
        acksRecps = nc_acks_receipts.ACKsReceipts(sharedState, mockDecoder)
        src_HWAddr = sharedState.get_my_hw_addr()
        src_ip = sharedState.get_my_ip_addr()

        recpcope_pkt = COPE_classes.COPE_packet()

        # ACKs packet 10, as well as (1100 0000), i.e. packets 2,3
        recpHeader = COPE_classes.ReportHeader(src_ip=src_ip, last_pkt=10, bit_map=192)
        recpcope_pkt.reports.append(recpHeader)
        acksRecps.processPkt(recpcope_pkt, src_HWAddr)

        self.assertTrue(10 in sharedState.neighbour_recp_rep[src_ip], "Pkt 10 was not found in neighbour_recp_rep")
        self.assertTrue(3 in sharedState.neighbour_recp_rep[src_ip], "Pkt 3 was not found in neighbour_recp_rep")
        self.assertTrue(2 in sharedState.neighbour_recp_rep[src_ip], "Pkt 2 was not found in neighbour_recp_rep")

        mockDecoder.decode.assert_called()

    # Failure testing: test response to invalid COPE packet
    def test_processPkt_invalidCOPEPkt(self):
        mockDecoder = mock.Mock()
        sharedState = nc_shared_state.SharedState()
        acksRecps = nc_acks_receipts.ACKsReceipts(sharedState, mockDecoder)
        src_HWAddr = sharedState.get_my_hw_addr()

        cope_pkt = None

        acksRecps.processPkt(cope_pkt, src_HWAddr)

        mockDecoder.decode.assert_not_called()

    def test_addACKSRecps(self):
        mockTransmitter = mock.Mock()
        sharedState = nc_shared_state.SharedState()
        addAcksRecps = nc_acks_receipts.AddACKsReceipts(sharedState, mockTransmitter)
        src_HWAddr = sharedState.get_my_hw_addr()
        src_ip = sharedState.get_my_ip_addr()
        cope_pkt = COPE_classes.COPE_packet()

        ackHeader = COPE_classes.ACKHeader(neighbour=src_HWAddr, last_ack=10, ack_map=192)
        recpHeader = COPE_classes.ReportHeader(src_ip=src_ip, last_pkt=10, bit_map=192)
        sharedState.ack_queue.append(ackHeader)
        sharedState.receipts_queue.append(recpHeader)

        addAcksRecps.addACKsRecps(cope_pkt)

        self.assertEqual(cope_pkt.acks[0], ackHeader, "ACKs were not equal")
        self.assertEqual(cope_pkt.reports[0], recpHeader, "Reports were not equal")

        mockTransmitter.transmit.assert_called()

    # # Long test
    # def test_ACKWaiter(self):
    #     cope_pkt = COPE_classes.COPE_packet()
    #     sharedState = nc_shared_state.SharedState()
    #     mockTransmitter = mock.Mock()
    #
    #     ack_waiter = nc_acks_receipts.ACKWaiter(cope_pkt, sharedState, mockTransmitter)
    #     ack_waiter.start()
    #
    #     time.sleep(4)
    #
    #     mockTransmitter.transmit.assert_called_with(cope_pkt)

    def test_ACKWaiter_waitTime(self):
        cope_pkt = COPE_classes.COPE_packet()
        sharedState = nc_shared_state.SharedState()
        mockTransmitter = mock.Mock()

        ack_waiter = nc_acks_receipts.ACKWaiter(cope_pkt, sharedState, mockTransmitter)
        ack_waiter.start()

        time.sleep(1)

        mockTransmitter.transmit.assert_not_called()
        ack_waiter.stopWaiter()

    def test_ACKWaiter_stop(self):
        cope_pkt = COPE_classes.COPE_packet()
        sharedState = nc_shared_state.SharedState()
        mockTransmitter = mock.Mock()

        ack_waiter = nc_acks_receipts.ACKWaiter(cope_pkt, sharedState, mockTransmitter)
        ack_waiter.start()
        ack_waiter.stopWaiter()

        mockTransmitter.transmit.assert_not_called()


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestACKRecps)
    unittest.TextTestRunner(verbosity=2).run(suite)
    logger.debug("Tests run")


if __name__ == '__main__':
    main()
