import unittest
import nc_shared_state
import nc_scheduler
from pypacker.layer12 import cope
from unittest.mock import Mock
import time
import logging.config
logging.config.fileConfig('logging.conf')
#logger =logging.getLogger('nc_node.test_ncscheduler')


class TestControlPktWaiter(unittest.TestCase):
    def test_sendControlPkt(self):
        mockPacketDispatcher = Mock()
        sharedState = nc_shared_state.SharedState()
        sharedState.setPacketDispatcher(mockPacketDispatcher)
        ackheader = cope.ACKHeader()
        sharedState.ack_queue.append(ackheader)
        controlPktWaiter = nc_scheduler.ControlPktWaiter(sharedState)
        controlPktWaiter.start()

        time.sleep(5)

        mockPacketDispatcher.dispatchControlPkt.assert_called()

    def test_NotsendControlPkt(self):
        mockPacketDispatcher = Mock()
        sharedState = nc_shared_state.SharedState()
        sharedState.setPacketDispatcher(mockPacketDispatcher)
        controlPktWaiter = nc_scheduler.ControlPktWaiter(sharedState)
        controlPktWaiter.start()

        time.sleep(5)

        mockPacketDispatcher.dispatchControlPkt.assert_not_called()

    def test_restartWaiter(self):
        mockPacketDispatcher = Mock()
        sharedState = nc_shared_state.SharedState()
        sharedState.setPacketDispatcher(mockPacketDispatcher)
        controlPktWaiter = nc_scheduler.ControlPktWaiter(sharedState)
        controlPktWaiter.start()

        time.sleep(3)
        controlPktWaiter.restartWaiter()
        time.sleep(3)

        mockPacketDispatcher.dispatchControlPkt.assert_not_called()


def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestControlPktWaiter)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #logger.debug("Tests run")


if __name__ == '__main__':
    main()
