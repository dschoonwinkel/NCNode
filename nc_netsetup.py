import logging
import logging.config
import json

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
        ip_to_mac_table[ip] = mac.upper()

    # logger.debug("IP to MAC table after read %s" % ip_to_mac_table)

    return ip_to_mac_table

def readNetworkRoutingJSON(ip_addr):
    with open('network_routing.json', 'r') as jsonfile:
        routing_dict = json.load(jsonfile)

    ip_to_mac_table = dict()

    for item in routing_dict[ip_addr]:
        ip_to_mac_table[item[0]] = item[1].upper()

    # print(ip_to_mac_table)

    return ip_to_mac_table

    

def writeNetworkConfig():
    addr_h1 = ('10.0.0.1','00:00:00:00:00:01')
    addr_h2 = ('10.0.0.2','00:00:00:00:00:02')
    addr_coding1 = ('10.0.1.1','00:00:ff:00:00:01')

    addr_dict = dict()
    addr_dict[addr_h1[0]] = [(addr_h2[0], addr_coding1[1])]
    addr_dict[addr_h2[0]] = [(addr_h2[0], addr_coding1[1])]
    addr_dict[addr_coding1[0]] = [addr_h1, addr_h2]

    print(addr_dict)

    with open('network_routing.json', 'w') as jsonfile:
        json.dump(addr_dict, jsonfile, indent=2)

def main():
    pass

if __name__ == '__main__':
    # main()
    writeNetworkConfig()
    print(readNetworkLayout())
    print(readNetworkRoutingJSON('10.0.1.1'))