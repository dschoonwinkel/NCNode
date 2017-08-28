import os.path, sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
import nc_shared_state

from nc_shared_state import SharedState
from nc_netw_listener import NetworkListener
from nc_acks_receipts import ACKsReceipts, AddACKsReceipts
from nc_decoder import Decoder
from nc_enqueuer import Enqueuer
from nc_stream_orderer import StreamOrderer
from nc_packet_dispatcher import PacketDispatcher
from nc_encoder import Encoder
from nc_transmitter import Transmitter
import COPE_packet_classes as COPE_classes
from nc_network_instance import NetworkInstanceAdapter
import logging
import logging.config

logging.config.fileConfig('logging.conf')
# logger =logging.getLogger('nc_node.ncRunner')
import time
import network_utils
import nc_encapsulator
import nc_udpstreamreader
import nc_app_instance
import pickle
import cProfile
import socket
import numpy as np

packetDispatcher = None
network_node_list = list(["10.0.0.1", "10.0.0.2"])
streamHandlers = list()

UDP_IP = "127.0.0.1"
UDP_PORT = 10002
MESSAGE = "Hello, World!"

#
# print("UDP target IP:", UDP_IP)
# print("UDP target port:", UDP_PORT)
# print("message:", MESSAGE)

sock = None


def setup_NCNode(sharedState):
    # Receiver side
    streamOrderer = StreamOrderer(sharedState)
    enqueuer = Enqueuer(sharedState, streamOrderer)
    decoder = Decoder(sharedState, enqueuer)
    acksReceipts = ACKsReceipts(sharedState, decoder)
    networkListener = NetworkListener(sharedState, acksReceipts)
    encapsulator = nc_encapsulator.Encapsulator(sharedState, enqueuer)

    # TODO: Improve this, this should not be hardcoded
    global network_node_list, streamHandlers
    print(sharedState.get_my_ip_addr())
    if sharedState.get_my_ip_addr() in network_node_list:
        network_node_list.remove(sharedState.get_my_ip_addr())
    # Start listener on each port that represents a node in the network
    for ip_addr in network_node_list:
        listener_port = network_utils.ipToListenerPort(ip_addr)
        # logger.debug("Starting streamHandler on ")
        streamHandler = nc_udpstreamreader.UDPStreamHandler(sharedState, listener_port, encapsulator)
        streamHandler.start()
        streamHandlers.append(streamHandler)

    # Sender side
    global packetDispatcher
    transmitter = Transmitter(sharedState)
    addACKsReceipts = AddACKsReceipts(sharedState, transmitter)
    encoder = Encoder(sharedState, addACKsReceipts)
    packetDispatcher = PacketDispatcher(sharedState, encoder)

    # Test with valid networkInstance
    networkInstanceAdapter = NetworkInstanceAdapter(network_utils.get_first_NicName())
    sharedState.networkInstance = networkInstanceAdapter
    appInstance = nc_app_instance.ApplicationInstanceAdapter()
    sharedState.appInstance = appInstance

    sharedState.setPacketDispatcher(packetDispatcher)


def test_receiver(sharedState):
    streamOrderer = StreamOrderer(sharedState)
    enqueuer = Enqueuer(sharedState, streamOrderer)
    decoder = Decoder(sharedState, enqueuer)
    acksReceipts = ACKsReceipts(sharedState, decoder)
    networkListener = NetworkListener(sharedState, acksReceipts)


def setup_sender(sharedState):
    global packetDispatcher
    transmitter = Transmitter(sharedState)
    addACKsReceipts = AddACKsReceipts(sharedState, transmitter)
    encoder = Encoder(sharedState, addACKsReceipts)
    packetDispatcher = PacketDispatcher(sharedState, encoder)

    # Test with valid networkInstance
    networkInstanceAdapter = NetworkInstanceAdapter(network_utils.get_first_NicName())
    sharedState.networkInstance = networkInstanceAdapter


def test_sender(sharedState):
#   global sock
    sharedState.times['Message sent'].append(time.time())
    sock.sendto(bytes(MESSAGE), (UDP_IP, UDP_PORT))

def main():
    global sock
    sharedState = SharedState()
    setup_NCNode(sharedState)
    # test_receiver(sharedState)
    # setup_sender(sharedState)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

    time.sleep(1)

    # logger.info("Starting Runner loop \n******************* \n\n\n*******************\n\n\n*******************")

    for i in range(10):
        test_sender(sharedState)
        time.sleep(1e-3)

    print("Send done")
    try:
        while (1):
            pass


    except KeyboardInterrupt:
        # logger.info("Closing gracefully")
        print("Closing gracefully")
        sharedState.run_event.clear()
        pass

        print("Times", sharedState.times)

        print("Sent to NC receive %s ms" % ((np.array(sharedState.times["Streamreader received"]) - np.array(sharedState.times['Message sent'])) * 1000))
        print("Average NC receive %s ms" % (np.mean(
        (np.array(sharedState.times["Streamreader received"]) - np.array(sharedState.times['Message sent'])) * 1000)))


        f = open("exec_times_%s.log" % network_utils.get_first_IPAddr(), 'w')
        pickle.dump(sharedState.times, f)


if __name__ == '__main__':
    main()
