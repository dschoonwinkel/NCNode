import subprocess
import scapy.all as scapy
import coding_utils
import logging
import logging.config

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("nc_node.network_utils")


def get_first_IPAddr():
    result = subprocess.check_output(["ifconfig"])
    # logger.debug('output = %s' % result)

    if result:
        addr_index = result.find("inet addr:")
        ip_addr = result[addr_index + len("inet addr:"):]
        ip_addr = ip_addr[:ip_addr.find(" ")]

        return ip_addr


def get_first_HWAddr():
    result = subprocess.check_output(["ifconfig"])
    # logger.debug('output = %s' % result)

    if result.find("HWaddr") == -1:
        logger.warn("HW Addr not found, using default")
        return "00:00:00:00:00:00"

    elif result:
        addr_index = result.find("HWaddr ")
        hw_addr = result[addr_index + len("HWaddr "):]
        hw_addr = hw_addr[:hw_addr.find(" ")]

        return hw_addr

def get_first_NicName():
    result = subprocess.check_output(["ifconfig"])
    # logger.debug('output = %s' % result)

    if result.find("HWaddr") == -1:
        logger.warn("HW Addr not found, therefore returning None")
        return None

    elif result:
        result = result.split(" ")
        hw_name = result[0]
        return hw_name


def get_HWAddr(ifacename):
    result = subprocess.check_output(["ifconfig", ifacename])
    # logger.debug(( 'output = %s' % result

    if result.find("HWaddr") == -1:
        logger.warn("HW Addr not found, using default")
        return "00:00:00:00:00:00"

    elif result:
        addr_index = result.find("HWaddr ")
        hw_addr = result[addr_index + len("HWaddr "):]
        hw_addr = hw_addr[:hw_addr.find(" ")]

        return hw_addr


def check_IPPacket(message_bytes):
    # Check minimum IP header size
    ip_pkt = None
    coding_utils.print_hex("Checking for IP packet", message_bytes)
    if len(message_bytes) >= 20:
        # logger.debug("Possible IP packet")
        ip_pkt = scapy.IP(message_bytes)
        # ip_pkt.show2()

        payload_len = len(ip_pkt.payload)
        # logger.debug("total_pkt_len", len(message_bytes))
        # logger.debug("header len", (len(message_bytes) - payload_len))
        # logger.debug("payload len", payload_len)
        # logger.debug("Checksum", scapy.utils.checksum(message_bytes[:-payload_len]))

        if scapy.utils.checksum(message_bytes[:-payload_len]) == 0:
            # logger.debug("Checksum correct")
            return ip_pkt

    return None


if __name__ == '__main__':
    ip_addr = get_first_IPAddr()
    hw_addr = get_first_HWAddr()
    hw_addr2 = get_HWAddr("eth0")
    logger.debug("Ip addr: %s" % str(ip_addr))
    logger.debug("HW addr: %s" % str(hw_addr))
    logger.debug("Eth0 HW addr: %s" % str(hw_addr2))
