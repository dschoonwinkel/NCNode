# Written for Python 3.4.3


import unittest
from unittest.mock import Mock
import nc_shared_state
import logging
import logging.config
import nc_netw_listener
import threading
logging.config.fileConfig('logging.conf')
import scapy.all as scapy
import COPE_packet_classes as COPE_classes
from pypacker.layer12 import ethernet, cope
from pypacker.layer3 import ip
import time


# logger =logging.getLogger('nc_node.test_ncpacketdispatcher')

class TestNetwListener(unittest.TestCase):

    def test_netwlisthelper_raiseException(self):
        # Send helper function
        def sendPkt():
            payload = b"\x00" * 100
            # self.#logger.debug("Sending packet on %s", self.iface)
            pkt = scapy.Ether(type=cope.COPE_PACKET_TYPE) / COPE_classes.COPE_packet() / payload
            scapy.sendp(pkt, iface='lo', verbose=0)


        sharedState = nc_shared_state.SharedState()
        mockListener = Mock()
        netwlistenerhelper = nc_netw_listener.NetworkListenerHelper(sharedState, mockListener)
        sharedState.setRunEvent()
        netwlistenerhelper.start()

        send_thread = threading.Thread(target=sendPkt)
        send_thread.start()

        time.sleep(0.1)
        sharedState.clearRunEvent()

        self.assertRaises(Exception)

    def test_netwlisthelper(self):
        # Send helper function
        def sendPkt():
            payload = b"\x00" * 100
            # self.#logger.debug("Sending packet on %s", self.iface)
            pkt = scapy.Ether(type=cope.COPE_PACKET_TYPE) / COPE_classes.COPE_packet() / payload
            pkt[COPE_classes.COPE_packet].calc_checksum()
            scapy.sendp(pkt, iface='lo', verbose=0)


        sharedState = nc_shared_state.SharedState()
        mockListener = Mock()
        netwlistenerhelper = nc_netw_listener.NetworkListenerHelper(sharedState, mockListener)
        sharedState.setRunEvent()
        netwlistenerhelper.start()

        send_thread = threading.Thread(target=sendPkt)
        send_thread.start()

        time.sleep(1)
        sharedState.clearRunEvent()

        self.assertTrue(mockListener.receivePkt.called)
        # print(mockListener.method_calls)
        self.assertEqual(mockListener.method_calls[0][0], "receivePkt")
        sent_pkt = mockListener.method_calls[0][1][0]
        self.assertEqual(type(sent_pkt), ethernet.Ethernet)

    def test_netwlisthelper_notCOPE(self):
        # Send helper function
        def sendPkt():
            payload = b"\x00" * 100
            # self.#logger.debug("Sending packet on %s", self.iface)
            pkt = scapy.Ether(type=0x800) / payload
            scapy.sendp(pkt, iface='lo', verbose=0)


        sharedState = nc_shared_state.SharedState()
        mockListener = Mock()
        netwlistenerhelper = nc_netw_listener.NetworkListenerHelper(sharedState, mockListener)
        sharedState.setRunEvent()
        netwlistenerhelper.start()

        send_thread = threading.Thread(target=sendPkt)
        send_thread.start()

        time.sleep(0.1)
        sharedState.clearRunEvent()

        self.assertFalse(mockListener.receivePkt.called)

    def test_netwListener_noInstance(self):
        mockACKs = Mock()
        sharedState = nc_shared_state.SharedState()
        netwListener = nc_netw_listener.NetworkListener(sharedState, mockACKs)

        self.assertIsNotNone(netwListener.networkInstance)

    def test_netwListener_Instance(self):
        mockACKs = Mock()
        mockNetwInstance = Mock()
        sharedState = nc_shared_state.SharedState()
        netwListener = nc_netw_listener.NetworkListener(sharedState, mockACKs, mockNetwInstance)

        self.assertEqual(netwListener.networkInstance, mockNetwInstance)

    def test_netwListener_receivePkt(self):
        mockACKs = Mock()
        mockNetwInstance = Mock()
        sharedState = nc_shared_state.SharedState()
        netwListener = nc_netw_listener.NetworkListener(sharedState, mockACKs, mockNetwInstance)

        pkt = ethernet.Ethernet(type=0x7123, src_s="12:23:34:45:56:67") + cope.COPE_packet() + ip.IP()
        pkt[cope.COPE_packet].calc_checksum()

        # print(pkt)
        netwListener.receivePkt(pkt)
        self.assertTrue(mockACKs.processPkt.called)
        self.assertEqual(mockACKs.method_calls[0][0], "processPkt")
        recv_pkt = mockACKs.method_calls[0][1][0]
        self.assertEqual(type(recv_pkt), cope.COPE_packet)
        self.assertEqual(pkt[cope.COPE_packet].bin(), recv_pkt.bin())
        self.assertEqual(mockACKs.method_calls[0][1][1], "12:23:34:45:56:67")




def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestNetwListener)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    main()