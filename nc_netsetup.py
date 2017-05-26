import logging
logging.config.fileConfig("logging.conf")
logger =logging.getLogger("nc_node.network_utils")

def readNetworkLayout():
    f = open('network_layout.net', 'r')
    contents = f.readlines()

    ip_to_mac_table = dict()

    for line in contents:
        split_line = line.split(" ")
        ip = split_line[0]
        mac = split_line[1][:-1]
        ip_to_mac_table[ip] = mac

    # logger.debug("IP to MAC table after read %s" % ip_to_mac_table)

    return ip_to_mac_table
