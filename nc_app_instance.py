import logging
import logging.config
import scapy.all as scapy
import COPE_packet_classes as COPE_classes
import socket
import network_utils
import coding_utils

class ApplicationInstanceAdapter(object):
    def __init__(self):
        logging.config.fileConfig('logging.conf')
        #self.#logger =logging.getLogger('nc_node.ApplicationInstanceAdapter')
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

    def trafficOut(self, pkt):


        # pkt.show2()
        #self.#logger.debug(coding_utils.print_hex("Pkt payload", str(pkt.payload)))
        ip_pkt = network_utils.check_IPPacket(str(pkt.payload))
        if ip_pkt:
            #ip_pkt.show2()
            my_ip = network_utils.get_first_IPAddr()
            localhost = "127.0.0.1"
            my_output_port = network_utils.ipToListenerPort(my_ip)
            message = str(ip_pkt[scapy.Raw])
            #self.#logger.debug("Sending packet on to application on my (IP, port) (%s, %d)" % (my_ip, my_output_port))
            #self.#logger.debug(coding_utils.print_hex("Message: ", message))

            self.sock.sendto(bytes(message), (localhost, my_output_port))

def main():
    pass



if __name__ == '__main__':
    main()