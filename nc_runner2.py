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
logger = logging.getLogger('nc_node.ncRunner')
import time
import scapy.all as scapy
import crc_funcs
import network_utils
import nc_encapsulator
import nc_udpstreamreader


packetDispatcher = None
network_node_list = list(["10.0.0.1", "10.0.0.2"])
streamHandlers = list()

def setup_NCNode(sharedState):
    # Receiver side
    streamOrderer = StreamOrderer(sharedState)
    enqueuer = Enqueuer(sharedState, streamOrderer)
    decoder = Decoder(sharedState, enqueuer)
    acksReceipts = ACKsReceipts(sharedState, decoder)
    networkListener = NetworkListener(sharedState, acksReceipts)

    # Input side
    sharedState.ip_to_mac["10.0.0.2"] = "00:00:00:00:00:02"
    sharedState.ip_to_mac["10.0.0.1"] = "00:00:00:00:00:01"
    encapsulator = nc_encapsulator.Encapsulator(sharedState, enqueuer)

    # TODO: Improve this, this should not be hardcoded
    global network_node_list, streamHandlers
    print sharedState.get_my_ip_addr()
    network_node_list.remove(sharedState.get_my_ip_addr())
    # Start listener on each port that represents a node in the network
    for ip_addr in network_node_list:
        listener_port = network_utils.ipToListenerPort(ip_addr)
        logger.debug("Starting streamHandler on ")
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

    cope_pkt = COPE_classes.COPE_packet()/scapy.IP()/scapy.Raw("NC Runner test")
    src_ip = sharedState.get_my_ip_addr()
    pkt_id_str = src_ip + str(1)
    pkt_id = crc_funcs.crc_hash(pkt_id_str)
    cope_pkt.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id, nexthop="00:00:00:00:00:02"))
    cope_pkt.reports.append(COPE_classes.ReportHeader(src_ip='10.0.0.2', last_pkt=90, bit_map=int('00001111', 2)))
    cope_pkt.local_pkt_seq_num = 1
    cope_pkt.calc_checksum()
    dstMAC = "00:00:00:00:00:02"
    cope_pkt.build()
    logger.debug("NC Runner: Encoded num %d" % len(cope_pkt.encoded_pkts))


    sharedState.addPacketToOutputQueue(dstMAC, cope_pkt)

    cope_pkt = COPE_classes.COPE_packet() / scapy.IP() / scapy.Raw("NC Runner test2")
    src_ip = sharedState.get_my_ip_addr()
    pkt_id_str = src_ip + str(2)
    pkt_id = crc_funcs.crc_hash(pkt_id_str)
    cope_pkt.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id, nexthop="00:00:00:00:00:02"))
    cope_pkt.reports.append(COPE_classes.ReportHeader(src_ip='10.0.0.2', last_pkt=91, bit_map=int('00011111', 2)))
    cope_pkt.local_pkt_seq_num = 2
    cope_pkt.calc_checksum()
    cope_pkt.show2()
    dstMAC = "00:00:00:00:00:02"
    sharedState.addPacketToOutputQueue(dstMAC, cope_pkt)
    packetDispatcher.dispatch()

def main():

    sharedState = SharedState()
    setup_NCNode(sharedState)
    # test_receiver(sharedState)
    # setup_sender(sharedState)

    time.sleep(2)



    logger.info("Starting Runner loop")
    try:
        while (1):
            raw_input()
            test_sender(sharedState)


    except KeyboardInterrupt:
        logger.info("Closing gracefully")


if __name__ == '__main__':
    main()