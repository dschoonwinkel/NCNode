from nc_shared_state import SharedState
from nc_netw_listener import NetworkListener
from nc_acks_receipts import ACKsReceipts, AddACKsReceipts
from nc_decoder import Decoder
from nc_enqueuer import Enqueuer
from nc_stream_orderer import StreamOrderer
from nc_packet_dispatcher import PacketDispatcher
from nc_encoder import Encoder
from nc_transmitter import Transmitter
from nc_network_instance import NetworkInstanceAdapter
from pypacker.layer12 import cope
from pypacker.layer3 import ip
import logging
import logging.config
logging.config.fileConfig('logging.conf')
#logger =logging.getLogger('nc_node.ncRunner')
import time
import crc_funcs
import network_utils
import nc_encapsulator
import nc_udpstreamreader
import nc_app_instance
import pickle
import asyncio

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
    # sharedState.ip_to_mac["10.0.0.2"] = "00:00:00:00:00:02"
    # sharedState.ip_to_mac["10.0.0.1"] = "00:00:00:00:00:01"
    # This is done by reading network config from python mininet topo script
    encapsulator = nc_encapsulator.Encapsulator(sharedState, enqueuer)

    # TODO: Improve this, this should not be hardcoded
    global network_node_list, streamHandlers

    print("My IP Addr: %s" % sharedState.get_my_ip_addr())
    print("My min_buffer_len: %d" % sharedState.min_buffer_len)


    # Remove node IP if in network node list:
    if sharedState.get_my_ip_addr() in network_node_list:
        network_node_list.remove(sharedState.get_my_ip_addr())


    # Start listener on each port that represents a node in the network
    for ip_addr in network_node_list:
        listener_port = network_utils.ipToListenerPort(ip_addr)
        #logger.debug("Starting streamHandler on ")
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
    appInstance = nc_app_instance.ApplicationInstanceAdapter(sharedState)
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

    cope_pkt = cope.COPE_packet() + ip.IP()
    cope_pkt.highest_layer.body_bytes = b"NC Runner test"
    src_ip = sharedState.get_my_ip_addr()
    pkt_id_str = src_ip + str(1)
    pkt_id = crc_funcs.crc_hash(pkt_id_str)
    cope_pkt.encoded_pkts.append(cope.EncodedHeader(pkt_id=pkt_id, nexthop_s="00:00:00:00:00:02"))
    cope_pkt.reports.append(cope.ReportHeader(src_ip_s='10.0.0.2', last_pkt=90, bit_map=int('00001111', 2)))
    cope_pkt.local_pkt_seq_num = 1
    cope_pkt.calc_checksum()
    dstMAC = "00:00:00:00:00:02"
    #logger.debug("NC Runner: Encoded num %d" % len(cope_pkt.encoded_pkts))


    sharedState.addPacketToOutputQueue(dstMAC, cope_pkt)

    cope_pkt = cope.COPE_packet() + ip.IP()
    cope_pkt.highest_layer.body_bytes = b"NC Runner test2"
    src_ip = sharedState.get_my_ip_addr()
    pkt_id_str = src_ip + str(2)
    pkt_id = crc_funcs.crc_hash(pkt_id_str)
    cope_pkt.encoded_pkts.append(cope.EncodedHeader(pkt_id=pkt_id, nexthop_s="00:00:00:00:00:02"))
    cope_pkt.reports.append(cope.ReportHeader(src_ip_s='10.0.0.2', last_pkt=91, bit_map=int('00011111', 2)))
    cope_pkt.local_pkt_seq_num = 2
    cope_pkt.calc_checksum()
    #cope_pkt.show2()
    dstMAC = "00:00:00:00:00:02"
    sharedState.addPacketToOutputQueue(dstMAC, cope_pkt)
    packetDispatcher.dispatch()

def main():

    sharedState = SharedState()
    setup_NCNode(sharedState)
    # test_receiver(sharedState)
    # setup_sender(sharedState)
    event_loop = asyncio.get_event_loop()
    sharedState.event_loop = event_loop

    time.sleep(0.5)



    #logger.info("Starting Runner loop \n******************* \n\n\n*******************\n\n\n*******************")
    try:
        # while (1):
        #     input()
        #     test_sender(sharedState)
        event_loop.run_forever()


    except KeyboardInterrupt:
        # logger.info("Closing gracefully")
        print("Closing gracefully")
        event_loop.close()
        pass

        # print "Times", sharedState.times
        f = open("exec_times_%s.log" % network_utils.get_first_IPAddr(), 'wb')
        pickle.dump(sharedState.times, f)


if __name__ == '__main__':
    main()