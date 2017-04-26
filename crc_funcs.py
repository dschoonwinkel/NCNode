import struct
import crcmod
import coding_utils
import logging
import logging.config

# data = "45 01 00 47 73 88 40 00 40 06 a2 c4 83 9f 0e 85 83 9f 0e a1"
# data = "00 01 70 A4 14 02 7B E9 C4 4E 0A 00 00 01 00 01 0A 00 00 02 00 00 00 00 00 00 00 5A 0F"
data = "00 01 70 A4 14 02 7B E9 C4 4E A2"

crc16 = crcmod.mkCrcFun(0x18005, rev="True", initCrc=0xFFFF, xorOut=0x0000)
crc64 = crcmod.predefined.mkCrcFun('crc-64')
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('nc_node.crcfuncs')

def crc_hash(msg):
    return crc64(msg)

def test_crchash():
    global data
    data_array = data.split()
    data_array = map(lambda x: int(x, 16), data_array)
    data_struct = struct.pack("%dB" % len(data_array), *data_array)
    logger.debug(' '.join('%02X' % ord(x) for x in data_struct))
    logger.debug("Crchash: 0x%04x" % crc_hash(data_struct))


def crc_checksum(msg):
    # Ignore last two bytes, i.e. checksum field
    # coding_utils.print_hex("\n\n #############################Checksum computation values: ", msg[:-2])
    return crc16(msg[:-2])


def test_crcchecksum():
    global data
    data = data.split()
    logger.debug(str(data))
    data = map(lambda x: int(x, 16), data)
    data = struct.pack("%dB" % len(data), *data)
    logger.debug(' '.join('%02X' % ord(x) for x in data))
    logger.debug("Checksum: 0x % 04x" % crc_checksum(data))

if __name__ == '__main__':
    test_crchash()
    test_crcchecksum()
