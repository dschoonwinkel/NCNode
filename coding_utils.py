from scapy.all import *
import COPE_packet_classes as COPE_classes
# import calculate_checksum
# from crc_checksum import *
import crc_funcs
import logging
import logging.config
logging.config.fileConfig('logging.conf')
#logger =logging.getLogger('codingUtils')


def print_hex(title, payload):
    hextext = title + ' '.join('%02X' % ord(x) for x in str(payload))
    logging.debug(hextext)
    return hextext


def extr_COPE_pkt(payload_bytes):
    cope_pkt = COPE_classes.COPE_packet(payload_bytes)
    raw_payload = None

    # cope_pkt.show2()
    # #logger.debug(len of cope_pkt.payload", len(cope_pkt.payload)
    # print_hex("Received cope packet", str(cope_pkt))
    # print_hex("Without payload     ", payload_bytes[:-len(cope_pkt.payload)])

    # #logger.debug(Checksum is correct: ", crc_funcs.crc_checksum(payload_bytes[:-len(cope_pkt.payload)]) == cope_pkt.checksum
    # #logger.debug(Checksum value: " , crc_funcs.crc_checksum(payload_bytes[:-len(cope_pkt.payload)])

    # Check if valid COPE packet, i.e. valid header checksum
    # If the payload length is 0, take the checksum of only the COPE packet header 
    if len(cope_pkt.payload) == 0 and crc_funcs.crc_checksum(payload_bytes) == cope_pkt.checksum:
        raw_payload = None
        return cope_pkt, raw_payload

    # Do a checksum of the header, i.e. all bytes without the payload bytes
    elif crc_funcs.crc_checksum(payload_bytes[:-len(cope_pkt.payload)]) != cope_pkt.checksum:
        logging.debug("I don't think it is a COPE_packet")
        return None, None

    # If it is a valid COPE packet and has a payload
    raw_payload = str(cope_pkt.payload)
    return cope_pkt, raw_payload


def COPE_to_str(cope_pkt):
    s = "COPE packet\n"
    s += "Enc Num: " + str(len(cope_pkt.encoded_pkts)) + "\n"
    for header in cope_pkt.encoded_pkts:
        s += "Encoded packet\n"
        s += "pkt_id = " + str(header.pkt_id) + "\n"
        s += "nexthop = " + str(header.nexthop) + "\n"

    s += "Report Num: " + str(cope_pkt.REPORT_NUM) + "\n"
    s += "Local_pkt_seq_num = " + str(cope_pkt.local_pkt_seq_num) + "\n"
    s += "Checksum = " + str(cope_pkt.checksum) + "\n"
    s += "Payload " + ' '.join('%02X' % ord(x) for x in str(cope_pkt.payload))

    return s


def strxor(s0, s1):
    if len(s0) > len(s1):
        s1 = s1 + '\0' * (len(s0) - len(s1))
    elif len(s1) > len(s0):
        s0 = s0 + '\0' * (len(s1) - len(s0))

    l = [chr(ord(a) ^ ord(b)) for a, b in zip(s0, s1)]
    return ''.join(l)
