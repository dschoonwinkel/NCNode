import logging
import logging.config
import socket
import network_utils
import nc_shared_state
from pypacker.layer12 import cope, ethernet
from pypacker.layer3 import ip

class ApplicationInstanceAdapter(object):
    def __init__(self, sharedState):
        logging.config.fileConfig('logging.conf')
        #self.#logger =logging.getLogger('nc_node.ApplicationInstanceAdapter')
        self.sharedState = sharedState
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

    def trafficOut(self, pkt):


        # pkt.show2()
        #self.#logger.debug(coding_utils.print_hex("Pkt payload", str(pkt.payload)))
        # TODO: This might be unnecessary, used in legacy scapy implementation to check for a data packet.
        ip_pkt = pkt[ip.IP]
        if ip_pkt:
            #ip_pkt.show2()
            my_ip = self.sharedState.get_my_ip_addr()
            localhost = "127.0.0.1"
            my_output_port = network_utils.ipToListenerPort(my_ip)
            message = ip_pkt.highest_layer.body_bytes
            #self.#logger.debug("Sending packet on to application on my (IP, port) (%s, %d)" % (my_ip, my_output_port))
            #self.#logger.debug(coding_utils.print_hex("Message: ", message))

            self.sock.sendto(bytes(message), (localhost, my_output_port))

def main():
    sharedState = nc_shared_state.SharedState()
    sharedState.my_ip_addr = "10.0.0.1"
    cope_pkt = cope.COPE_packet()
    encap_pkt = ethernet.Ethernet() + cope_pkt + ip.IP()
    encap_pkt.highest_layer.body_bytes = b"nc_netw_inst_test packet"

    appInstance = ApplicationInstanceAdapter(sharedState)
    appInstance.trafficOut(encap_pkt)



if __name__ == '__main__':
    main()