import unittest
import coding_utils
import logging
import logging.config
logging.config.fileConfig('logging.conf')
#logger =logging.getLogger('nc_node.test_codingutils')

class TestCodingUtils(unittest.TestCase):

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

	def test_bytexor1(self):
		str1 = b"\xde\xad\xbe\xef"
		str2 = b"\xca\xfe\xbe\xed\xed"

		result = coding_utils.bytexor(str1, str2)
		# coding_utils.print_hex("Coded result: ", result)
		self.assertEqual(result, b"\x14\x53\x00\x02\xed", "XORed Strings do not match")

	def test_bytexor2(self):
		str1 = b"\xde\xad\xbe\xef"
		str2 = b"\xca\xfe\xbe\xed\xed"

		result = coding_utils.bytexor(str1, str2)
		self.assertEqual(result, b"\x14\x53\x00\x02\xed", "XORed Strings do not match")


	def test_bytexor3(self):
		str1 = b"Hello"
		str2 = b"Greener"

		result = coding_utils.bytexor(str1, str2)
		# coding_utils.print_hex("Coded result: ", result)
		self.assertEqual(result, b"\x0f\x17\x09\x09\x01er", "XORed Strings do not match")
		

def main():
	suite = unittest.TestLoader().loadTestsFromTestCase(TestCodingUtils)
	unittest.TextTestRunner(verbosity=2).run(suite)
	#logger.debug("Tests run")

if __name__ == '__main__':
	main()