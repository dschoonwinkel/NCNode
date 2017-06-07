import subprocess
import coding_utils
import logging
import logging.config
import re
import netifaces

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
            return hw_addr.upper()

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
                return hw_addr.upper()

    return None


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


