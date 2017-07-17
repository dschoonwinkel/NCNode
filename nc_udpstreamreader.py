import socket
import threading
import logging
import logging.config
import nc_shared_state
import nc_encapsulator
import nc_enqueuer
import nc_stream_orderer
import time
import pickle
import network_utils
logging.config.fileConfig('logging.conf')

class UDPPortToIP(object):

    port_to_IP = dict()
    port_to_IP[10001] = "10.0.0.1"
    port_to_IP[10002] = "10.0.0.2"
    port_to_IP[10900] = "10.0.0.1"

    @staticmethod
    def ip_from_udpport(portnumber):
        return UDPPortToIP.port_to_IP[portnumber]

class UDPStreamHandler(threading.Thread):

    def __init__(self, sharedState, listening_port, encapsulator):
        threading.Thread.__init__(self)
        self.sharedState = sharedState
        self.encapsulator = encapsulator
        self.listening_port = listening_port
        self.listening_addr = "127.0.0.1"
        self.stop_event = threading.Event()
        self.daemon = True
        self.logger =logging.getLogger('nc_node.UDPStreamHandler')

    def run(self):
        sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
        sock.bind((self.listening_addr, self.listening_port))

        self.logger.debug("Starting UDPStreamReader on %d" % self.listening_port)
        while self.sharedState.run_event.is_set():
            data, addr = sock.recvfrom(65565) # buffer size is 65535 bytes
            # Send the data to the encapsulator
            self.logger.debug(coding_utils.print_hex("Received data", data))

            self.sharedState.times["Streamreader received"].append(time.time())
            self.encapsulator.encapsulate(data, UDPPortToIP.ip_from_udpport(self.listening_port))

def main():
    sharedState = nc_shared_state.SharedState()
    sharedState.ip_to_mac["10.0.0.2"] = "00:00:00:00:00:02"
    sharedState.ip_to_mac["10.0.0.1"] = "00:00:00:00:00:01"
    streamOrderer = nc_stream_orderer.StreamOrderer(sharedState)
    enqueuer = nc_enqueuer.Enqueuer(sharedState, streamOrderer)
    encapsulator = nc_encapsulator.Encapsulator(sharedState, enqueuer)

    streamHandler = UDPStreamHandler(sharedState, 10900, encapsulator)
    streamHandler.start()

    try:
        while (1):
            pass

    except KeyboardInterrupt:
        sharedState.stopWaiters()
        print("Closing gracefully")
        print(sharedState.times)
        f = open("exec_times_%s.log" % network_utils.get_first_IPAddr(), 'w')
        pickle.dump(sharedState.times, f)


if __name__ == '__main__':
    main()
