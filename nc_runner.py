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
import logging
import logging.config
logging.config.fileConfig('logging.conf')
#logger =logging.getLogger('nc_node.ncRunner')
from pypacker.layer12 import ethernet, cope
from pypacker.layer3 import ip
import time
import crc_funcs
import network_utils

def test_receiver(sharedState):
    
    streamOrderer = StreamOrderer(sharedState)
    enqueuer = Enqueuer(sharedState, streamOrderer)
    decoder = Decoder(sharedState, enqueuer)
    acksReceipts = ACKsReceipts(sharedState, decoder)
    networkListener = NetworkListener(sharedState, acksReceipts)

def test_sender(sharedState):
    
    
    transmitter = Transmitter(sharedState)
    addACKsReceipts = AddACKsReceipts(sharedState, transmitter)
    encoder = Encoder(sharedState, addACKsReceipts)
    packetDispatcher = PacketDispatcher(sharedState, encoder)
    
    # Test with valid networkInstance
    networkInstanceAdapter = NetworkInstanceAdapter(network_utils.get_first_NicName())
    sharedState.networkInstance = networkInstanceAdapter
    
    cope_pkt = cope.COPE_packet() + ip.IP()
    cope_pkt.highest_layer.body_bytes = b"NC Runner test"
    src_ip = sharedState.get_my_ip_addr()
    pkt_id_str = src_ip + str(1)
    pkt_id = crc_funcs.crc_hash(pkt_id_str)
    cope_pkt.encoded_pkts.append(cope.EncodedHeader(pkt_id=pkt_id, nexthop_s="00:00:00:00:00:02"))
    cope_pkt.reports.append(cope.ReportHeader(src_ip_s='10.0.0.2', last_pkt=90, bit_map=int('00001111', 2)))
    cope_pkt.local_pkt_seq_num = 1
    dstMAC = "00:00:00:00:00:01"
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
    #cope_pkt.show2()
    dstMAC = "00:00:00:00:00:01"
    sharedState.addPacketToOutputQueue(dstMAC, cope_pkt)
    packetDispatcher.dispatch()
    
    


def main():

    sharedState = SharedState()
    test_receiver(sharedState)
    time.sleep(2)
    test_sender(sharedState)



    #logger.info("Starting Runner loop")
    try:
        while True:
            pass

    except KeyboardInterrupt:
        #logger.info("Closing graciously")
        pass
        

if __name__ == '__main__':
    main()