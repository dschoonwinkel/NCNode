import logging
import logging.config
from pypacker import psocket
from pypacker.layer12 import cope, ethernet
import network_utils
logging.config.fileConfig('logging.conf')

class NetworkInstanceAdapter(object):
    
    def __init__(self, iface):
        self.iface = iface

        self.logger =logging.getLogger('nc_node.NetworkInstanceAdapter')
        self.psock = psocket.SocketHndl(iface_name=iface, mode=psocket.SocketHndl.MODE_LAYER_2)
    
    def sendPkt(self, pkt):
        self.logger.debug("Sending packet on %s" % self.iface)
        self.psock.send(pkt.bin())
    
def main():
    networkInstance = NetworkInstanceAdapter(network_utils.get_first_NicName())
    cope_pkt = cope.COPE_packet()
    encap_pkt = ethernet.Ethernet() + cope_pkt
    encap_pkt[cope.COPE_packet].body_bytes = b"nc_netw_inst_test packet"
    networkInstance.sendPkt(encap_pkt)

if __name__ == '__main__':
    main()