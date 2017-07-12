import unittest
import nc_shared_state
import nc_acks_receipts
from pypacker.layer12 import cope
from unittest.mock import Mock
import time
import nc_acks_receipts
import logging
import logging.config
logging.config.fileConfig('logging.conf')
#logger =logging.getLogger('nc_node.test_ncacksreceipt')


class TestACKRecps(unittest.TestCase):
    def test_processPkt_ack(self):
        mockDecoder = Mock()
        sharedState = nc_shared_state.SharedState()
        acksRecps = nc_acks_receipts.ACKsReceipts(sharedState, mockDecoder)
        src_HWAddr = sharedState.get_my_hw_addr()
        neighbourMAC = "00:00:00:00:00:02"

        # Set up ACKWaiters
        mockACKWaiter_pkt10 = Mock()
        mockACKWaiter_pkt2 = Mock()
        mockACKWaiter_pkt3 = Mock()

        sharedState.addACK_waiter(neighbourMAC, 10, mockACKWaiter_pkt10)
        sharedState.addACK_waiter(neighbourMAC, 3, mockACKWaiter_pkt3)
        sharedState.addACK_waiter(neighbourMAC, 2, mockACKWaiter_pkt2)

        # print(sharedState.ack_waiters)

        ackcope_pkt = cope.COPE_packet()

        # ACKs packet 10, as well as (1100 0000), i.e. packets 2,3
        ackHeader = cope.ACKHeader(neighbour_s=src_HWAddr, last_ack=10, ack_map=192)
        ackcope_pkt.acks.append(ackHeader)
        acksRecps.processPkt(ackcope_pkt, neighbourMAC)

        mockACKWaiter_pkt10.stopWaiter.assert_called()
        mockACKWaiter_pkt3.stopWaiter.assert_called()
        mockACKWaiter_pkt2.stopWaiter.assert_called()

        mockDecoder.decode.assert_called()

    def test_processPkt_recp(self):
        mockDecoder = Mock()
        sharedState = nc_shared_state.SharedState()
        acksRecps = nc_acks_receipts.ACKsReceipts(sharedState, mockDecoder)
        sharedState.my_ip_addr = "10.0.0.1"
        src_HWAddr = sharedState.get_my_hw_addr()
        src_ip = sharedState.get_my_ip_addr()

        recpcope_pkt = cope.COPE_packet()

        # ACKs packet 10, as well as (1100 0000), i.e. packets 2,3
        recpHeader = cope.ReportHeader(src_ip_s=src_ip, last_pkt=10, bit_map=192)
        recpcope_pkt.reports.append(recpHeader)
        acksRecps.processPkt(recpcope_pkt, src_HWAddr)

        # print(sharedState.neighbour_recp_rep.keys())

        self.assertTrue(10 in sharedState.neighbour_recp_rep[src_ip], "Pkt 10 was not found in neighbour_recp_rep")
        self.assertTrue(3 in sharedState.neighbour_recp_rep[src_ip], "Pkt 3 was not found in neighbour_recp_rep")
        self.assertTrue(2 in sharedState.neighbour_recp_rep[src_ip], "Pkt 2 was not found in neighbour_recp_rep")

        mockDecoder.decode.assert_called()

    # Failure testing: test response to invalid COPE packet
    def test_processPkt_invalidCOPEPkt(self):
        mockDecoder = Mock()
        sharedState = nc_shared_state.SharedState()
        acksRecps = nc_acks_receipts.ACKsReceipts(sharedState, mockDecoder)
        src_HWAddr = sharedState.get_my_hw_addr()

        cope_pkt = None

        acksRecps.processPkt(cope_pkt, src_HWAddr)

        mockDecoder.decode.assert_not_called()

    def test_addACKSRecps(self):
        mockTransmitter = Mock()
        sharedState = nc_shared_state.SharedState()
        addAcksRecps = nc_acks_receipts.AddACKsReceipts(sharedState, mockTransmitter)
        src_HWAddr = sharedState.get_my_hw_addr()
        sharedState.my_ip_addr = "10.0.0.1"
        src_ip = sharedState.get_my_ip_addr()
        cope_pkt = cope.COPE_packet()

        ackHeader = cope.ACKHeader(neighbour_s=src_HWAddr, last_ack=10, ack_map=192)
        recpHeader = cope.ReportHeader(src_ip_s=src_ip, last_pkt=10, bit_map=192)
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
        cope_pkt = cope.COPE_packet()
        sharedState = nc_shared_state.SharedState()
        mockTransmitter = Mock()

        ack_waiter = nc_acks_receipts.ACKWaiter(cope_pkt, sharedState, mockTransmitter)
        ack_waiter.start()

        time.sleep(1)

        mockTransmitter.transmit.assert_not_called()
        ack_waiter.stopWaiter()

    def test_ACKWaiter_stop(self):
        cope_pkt = cope.COPE_packet()
        sharedState = nc_shared_state.SharedState()
        mockTransmitter = Mock()

        ack_waiter = nc_acks_receipts.ACKWaiter(cope_pkt, sharedState, mockTransmitter)
        ack_waiter.start()
        ack_waiter.stopWaiter()

        mockTransmitter.transmit.assert_not_called()


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestACKRecps)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #logger.debug("Tests run")


if __name__ == '__main__':
    main()
