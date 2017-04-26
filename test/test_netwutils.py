import unittest
import logging
import logging.config
import nc_shared_state
import COPE_packet_classes as COPE_classes
import scapy.all as scapy
import network_utils

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('nc_node.ncDecoder')

class TestNetworkUtils(unittest.TestCase):

	def test_checkIPPacket(self):
		pkt = scapy.IP()/scapy.Raw("Hello!")
		# pkt.show2()
		ip_pkt = network_utils.check_IPPacket(str(pkt))
		# ip_pkt.show2()
		self.assertEqual(str(pkt), str(ip_pkt), "Incorrect IP packet extracted")


	def test_checkIPPacket_invalid(self):
		pkt = scapy.Raw("A"*20)/scapy.Raw("Hello!")
		# pkt.show2()
		ip_pkt = network_utils.check_IPPacket(str(pkt))
		self.assertEqual(None, ip_pkt, "Extracted Ip packet was not null")

	def test_getNicName(self):
		hw_name = network_utils.get_first_NicName()
		self.assertEqual(hw_name, "h1-eth0")
		# self.assertEqual(hw_name, "eth0")
		self.assertNotEqual(hw_name, "lo", )

def main():
	suite = unittest.TestLoader().loadTestsFromTestCase(TestNetworkUtils)
	unittest.TextTestRunner(verbosity=2).run(suite)
	logger.debug("Tests run")

if __name__ == '__main__':
	main()