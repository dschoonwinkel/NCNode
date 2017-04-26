import logging
import logging.config
import scapy.all as scapy
import COPE_packet_classes as COPE_classes


class NetworkInstanceAdapter(object):
    
    def __init__(self, iface):
        self.iface = iface
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('nc_node.NetworkInstanceAdapter')
    
    def sendPkt(self, pkt):
        self.logger.debug("Sending packet on %s", self.iface)
        scapy.sendp(pkt, iface=self.iface, verbose=0)
    
def main():
    networkInstance = NetworkInstanceAdapter("eth0")
    cope_pkt = COPE_classes.COPE_packet()
    encap_pkt = scapy.Ether()/cope_pkt/scapy.Raw("nc_netw_inst_test packet")
    networkInstance.sendPkt(encap_pkt)

if __name__ == '__main__':
    main()