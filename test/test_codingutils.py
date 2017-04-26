import unittest
import nc_shared_state
import COPE_packet_classes as COPE_classes
import scapy.all as scapy
import coding_utils
import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('nc_node.test_codingutils')

class TestCodingUtils(unittest.TestCase):

	def test_extr_COPE_pkt(self):
		cope_pkt = COPE_classes.COPE_packet()
		cope_pkt.calc_checksum()
		pkt, payload = coding_utils.extr_COPE_pkt(str(cope_pkt))
		# coding_utils.print_hex("Original cope packet ", str(cope_pkt))
		# coding_utils.print_hex("Retrieved cope packet", str(cope_pkt))
		# self.assertEqual(pkt, cope_pkt, "Invalid cope_header")  --- This is not equal, as it refers to different objects with the same content
		# 1. Test for empty payload and valid COPE packet
		# self.assertEqual(str(pkt), str(cope_pkt), "1. Invalid cope_header")

		raw_payload = "Hello"

		# 2. Test for valid COPE packet and payload
		encap_pkt = cope_pkt/scapy.Raw(raw_payload)
		pkt, payload = coding_utils.extr_COPE_pkt(str(encap_pkt))
		# coding_utils.print_hex("Original cope packet ", str(encap_pkt))
		# coding_utils.print_hex("Retrieved cope packet ", str(pkt))
		# coding_utils.print_hex("Retrieved payload ", str(payload))
		self.assertEqual(str(encap_pkt), str(pkt), "2. Incorrect cope_pkt")
		self.assertEqual(raw_payload, payload, "2. Incorrect payload")

		# # 3. Test for valid COPE packet and IP encaps
		# encap_pkt = cope_pkt/scapy.IP()/scapy.Raw(raw_payload)
		# pkt, payload = coding_utils.extr_COPE_pkt(str(encap_pkt))
		# self.assertEqual(str(encap_pkt), str(pkt), "3. Incorrect cope_pkt")
		# self.assertEqual(str(encap_pkt)[len(str(cope_pkt)):], payload, "3. Incorrect payload")

		# # 4. Test for valid COPE packet, and valid IP / TCP stack
		# encap_pkt = cope_pkt/scapy.IP()/scapy.TCP()/scapy.Raw(raw_payload)
		# pkt, payload = coding_utils.extr_COPE_pkt(str(encap_pkt))
		# self.assertEqual(str(encap_pkt), str(pkt), "4. Incorrect cope_pkt")
		# self.assertEqual(str(encap_pkt)[len(str(cope_pkt)):], payload, "4. Incorrect payload")

		# # 5. Test for invalid COPE packet with valid IP encaps
		# cope_pkt = scapy.Raw("1" * 12)
		# encap_pkt = cope_pkt / scapy.Raw(raw_payload)
		# pkt, payload = coding_utils.extr_COPE_pkt(str(encap_pkt))
		# self.assertEqual(None, pkt, "5. Incorrect cope_pkt")
		# self.assertEqual(None, payload, "5. Incorrect payload")

	def test_strxor1(self):
		str1 = "\xde\xad\xbe\xef"
		str2 = "\xca\xfe\xbe\xed\xed"

		result = coding_utils.strxor(str1, str2)
		# coding_utils.print_hex("Coded result: ", result)
		self.assertEqual(result, "\x14\x53\x00\x02\xed", "XORed Strings do not match")

	def test_strxor2(self):
		str1 = "\xde\xad\xbe\xef"
		str2 = "\xca\xfe\xbe\xed\xed"

		result = coding_utils.strxor(str1, str2)
		self.assertEqual(result, "\x14\x53\x00\x02\xed", "XORed Strings do not match")


	def test_strxor3(self):
		str1 = "Hello"
		str2 = "Greener"

		result = coding_utils.strxor(str1, str2)
		# coding_utils.print_hex("Coded result: ", result)
		self.assertEqual(result, "\x0f\x17\x09\x09\x01er", "XORed Strings do not match")
		

def main():
	suite = unittest.TestLoader().loadTestsFromTestCase(TestCodingUtils)
	unittest.TextTestRunner(verbosity=2).run(suite)
	logger.debug("Tests run")

if __name__ == '__main__':
	main()