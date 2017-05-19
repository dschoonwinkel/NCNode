import unittest
import nc_shared_state
import COPE_packet_classes as COPE_classes
import scapy.all as scapy
import coding_utils
import nc_transmitter
import mock
import logging
import logging.config
logging.config.fileConfig('logging.conf')
#logger =logging.getLogger('nc_node.test_nctransmitter')

class TestTransmitter(unittest.TestCase):

	def test_transmit_native(self):
		mockNetwInst = mock.Mock()
		sharedState = nc_shared_state.SharedState()
		sharedState.networkInstance = mockNetwInst
		transmitter = nc_transmitter.Transmitter(sharedState)
		hw_dest1 = "00:00:00:00:00:01"
		header1 = COPE_classes.EncodedHeader(pkt_id=1, nexthop=hw_dest1)

		cope_pkt = COPE_classes.COPE_packet()
		# print mockNetwInst.sendPkt.call_args_list
		# mockNetwInst.sendPkt.call_args_list[0][0][0].show2()

		# Packet contains no headers, i.e. control packet
		transmitter.transmit(cope_pkt)
		sent_pkt = mockNetwInst.sendPkt.call_args_list[0][0][0]
		self.assertEqual(sent_pkt.type, COPE_classes.COPE_PACKET_TYPE, "Incorrect packet type")
		self.assertEqual(str(sent_pkt.payload), str(cope_pkt), "Encapsulation failed native")
		self.assertEqual(sharedState.native_packets_sent, 0)
		self.assertEqual(sharedState.encoded_packets_sent, 0)

		# Packet contains 1 header, i.e. native packet
		cope_pkt.encoded_pkts.append(header1)
		# print mockNetwInst.sendPkt.call_args_list
		transmitter.transmit(cope_pkt)
		sent_pkt = mockNetwInst.sendPkt.call_args_list[1][0][0]
		self.assertEqual(sent_pkt.type, COPE_classes.COPE_PACKET_TYPE, "Incorrect packet type")
		self.assertEqual(str(sent_pkt.payload), str(cope_pkt), "Encapsulation failed native")
		self.assertEqual(sharedState.native_packets_sent, 1)
		self.assertEqual(sharedState.encoded_packets_sent, 0)

		# Packet now contains 2 headers, i.e. encoded packet
		cope_pkt.encoded_pkts.append(header1)
		transmitter.transmit(cope_pkt)
		sent_pkt = mockNetwInst.sendPkt.call_args_list[2][0][0]
		self.assertEqual(sent_pkt.type, COPE_classes.COPE_PACKET_TYPE, "Incorrect packet type")
		self.assertEqual(str(sent_pkt.payload), str(cope_pkt), "Encapsulation failed enc")
		self.assertEqual(sharedState.native_packets_sent, 1)
		self.assertEqual(sharedState.encoded_packets_sent, 1)

		# Packet now contains 4 headers
		cope_pkt.encoded_pkts.append(header1)
		cope_pkt.encoded_pkts.append(header1)
		transmitter.transmit(cope_pkt)
		sent_pkt = mockNetwInst.sendPkt.call_args_list[3][0][0]
		self.assertEqual(sent_pkt.type, COPE_classes.COPE_PACKET_TYPE, "Incorrect packet type")
		self.assertEqual(str(sent_pkt.payload), str(cope_pkt), "Encapsulation failed enc")
		self.assertEqual(sharedState.native_packets_sent, 1)
		self.assertEqual(sharedState.encoded_packets_sent, 2)
		

def main():
	suite = unittest.TestLoader().loadTestsFromTestCase(TestTransmitter)
	unittest.TextTestRunner(verbosity=2).run(suite)
	#logger.debug("Tests run")

if __name__ == '__main__':
	main()