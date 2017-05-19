import subprocess
import scapy.all as scapy
import coding_utils
import logging
import logging.config
import re
import netifaces
import COPE_packet_classes as COPE_classes

logging.config.fileConfig("logging.conf")
#logger =logging.getLogger("nc_node.network_utils")


def get_first_IPAddr():
    ifaces = netifaces.interfaces()
    if 'lo' in ifaces:
        ifaces.remove('lo')
    addrs = netifaces.ifaddresses(ifaces[0])

    # print ifaces
    # print addrs

    if netifaces.AF_INET in addrs:
        # print addrs[netifaces.AF_INET][0]['addr']
        if 'addr' in addrs[netifaces.AF_INET][0]:
            ip_addr = addrs[netifaces.AF_INET][0]['addr']
            return ip_addr

    # The first ip addr was not found
    return None

def get_first_HWAddr():
    ifaces = netifaces.interfaces()
    if 'lo' in ifaces:
        ifaces.remove('lo')
    addrs = netifaces.ifaddresses(ifaces[0])

    if netifaces.AF_PACKET in addrs:
        # print addrs[netifaces.AF_PACKET][0]['addr']
        if 'addr' in addrs[netifaces.AF_PACKET][0]:
            hw_addr = addrs[netifaces.AF_PACKET][0]['addr']
            return hw_addr

    return None

def get_first_NicName():
    ifaces = netifaces.interfaces()
    if 'lo' in ifaces:
        ifaces.remove('lo')
    if len(ifaces) >= 0:
        return ifaces[0]

    # The first ip addr was not found
    return None

def get_HWAddr(ifacename):
    ifaces = netifaces.interfaces()
    if 'lo' in ifaces:
        ifaces.remove('lo')

    if ifacename in ifaces:
        addrs = netifaces.ifaddresses(ifacename)

        if netifaces.AF_PACKET in addrs:
            # print addrs[netifaces.AF_PACKET][0]['addr']
            if 'addr' in addrs[netifaces.AF_PACKET][0]:
                hw_addr = addrs[netifaces.AF_PACKET][0]['addr']
                return hw_addr

    return None


def check_IPPacket(message_bytes):
    # Check minimum IP header size
    ip_pkt = None
    message_bytes = str(message_bytes)
    # #logger.debug(coding_utils.print_hex("Checking for IP packet", message_bytes))
    if len(message_bytes) >= 20:
        # #logger.debug("Possible IP packet")
        ip_pkt = scapy.IP(message_bytes)

        payload_len = len(ip_pkt.payload)
        # #logger.debug("total_pkt_len", len(message_bytes))
        # #logger.debug("header len", (len(message_bytes) - payload_len))
        # #logger.debug("payload len", payload_len)
        # #logger.debug("Checksum", scapy.utils.checksum(message_bytes[:-payload_len]))

        # If zero payload len is not treated correctly, entire packet is removed in substring error
        if payload_len == 0:
            if scapy.utils.checksum(message_bytes) == 0:
                return ip_pkt

        if scapy.utils.checksum(message_bytes[:-payload_len]) == 0:
            # #logger.debug("Checksum correct")
            return ip_pkt

    return None

def dissectCOPE_pkt(ether_pkt):
    cope_pkt = None
    ip_pkt = None
    raw_data = None
    # It is not a cope packet
    if ether_pkt.type != 0x7123:
        return cope_pkt, ip_pkt, raw_data

    cope_pkt, raw_ip = coding_utils.extr_COPE_pkt(str(ether_pkt.payload))
    if not cope_pkt:
        #logger.error("COPE packet was None")
        return cope_pkt, ip_pkt, raw_data

    ip_pkt = check_IPPacket(str(cope_pkt.payload))

    if not ip_pkt:
        #logger.error("IP packet was None")
        return cope_pkt, ip_pkt, raw_data

    raw_data = str(ip_pkt[scapy.Raw])

    return cope_pkt, ip_pkt, raw_data



def ipToListenerPort(ip_addr):
    ip_addr = str(ip_addr)
    port_str = re.sub('[.]', '', ip_addr)
    return int(port_str)


if __name__ == '__main__':
    ip_addr = get_first_IPAddr()
    hw_addr = get_first_HWAddr()
    # hw_addr2 = get_HWAddr("eth0")
    # hw_addr2 = get_HWAddr("h1-eth0")
    # hw_addr2 = get_HWAddr("h2-eth0")
    #logger.debug("Ip addr: %s" % str(ip_addr))
    #logger.debug("HW addr: %s" % str(hw_addr))
    # #logger.debug("Eth0 HW addr: %s" % str(hw_addr2))
    #logger.debug("Port number %d" % ipToListenerPort(ip_addr))


