import logging
import logging.config

from nc_shared_state import SharedState
from nc_enqueuer import Enqueuer
from nc_stream_orderer import StreamOrderer
import scapy.all as scapy
import crc_funcs
import coding_utils
import COPE_packet_classes as COPE_classes

debug = True

class Decoder(object):

    def __init__(self, sharedState, enqueuer):
        self.sharedState = sharedState
        self.enqueuer = enqueuer
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('nc_node.ncDecoder')
        # self.logger.critical("Starting ncDecoderLogger")

    def decode(self, cope_pkt, from_neighbour):
        self.logger.debug("Got packet to decode")
        # Decode the COPE packets contained in this packet
        # Schedule ACKs and receipt reports
        # ACK or Reception packet

        self.logger.debug("Encoded NUM %d" % len(cope_pkt.encoded_pkts))
        if len(cope_pkt.encoded_pkts) == 0:
            # No packets to decode
            return True

        # Native packet
        elif len(cope_pkt.encoded_pkts) == 1:

            # Check if I must process it
            if cope_pkt.encoded_pkts[0].nexthop == self.sharedState.get_my_hw_addr():

                self.logger.info("Native packet decoded")
                # self.logger.debug("Uncoded pkt: putting pkt_id in packet_ids_recv set")
                pkt_id = cope_pkt.encoded_pkts[0].pkt_id
                # self.logger.debug("Pkt_id %d" % pkt_id)
                self.sharedState.addPacketToPacketPool(pkt_id, cope_pkt)
                # Do ACK scheduling here
                # self.logger.info("Uncoded pkt seen: %d, received %d" % (len(self.sharedState.pkts_ids_received), packets_received))
                if from_neighbour == self.sharedState.get_my_hw_addr():
                    self.logger.debug("Overheard locally, do not schedule ACK")

                else:
                    self.sharedState.scheduleACK(from_neighbour, cope_pkt.local_pkt_seq_num)

                # Let other nodes know that I have received this packet
                self.sharedState.scheduleReceipts(cope_pkt)


                self.enqueuer.enqueue(cope_pkt)
                return True

            # I am not the nexthop, keep the packet for decoding other packets
            else:
                self.logger.debug("Native packet stored")
                pkt_id = cope_pkt.encoded_pkts[0].pkt_id
                self.sharedState.addPacketToPacketPool(pkt_id, cope_pkt)

        # Encoded packet, check if one of the packet are meant for me
        elif len(cope_pkt.encoded_pkts) >= 2 and cope_pkt.check_nexthops(self.sharedState.get_my_hw_addr()):
            self.logger.debug("Got encoded packet")
            decoded_payload = ""
            missing_headers = list()
            for header in cope_pkt.encoded_pkts:
                if header.pkt_id not in self.sharedState.packet_ids_recv:
                    self.logger.debug("Packet " +str(header.pkt_id) + " not found for decoding")
                    missing_headers.append(header)
                    
                    if len(missing_headers) > 1:
                        self.logger.error("Not decodable")
                        return False

                else:
                    decoded_payload = coding_utils.strxor(decoded_payload, str(self.sharedState.getPacketFromPacketPool(header.pkt_id).payload))
                                        

            

            # If len = 0, no new native packets were discovered, if more than 1, undecodable
            if len(missing_headers) == 1:
                hex_text = coding_utils.print_hex("Decoded payload", decoded_payload)
                self.logger.debug("Decoded payload: " + hex_text)
                decoded_native_pkt = COPE_classes.COPE_packet()
                decoded_native_pkt.encoded_pkts.append(missing_headers[0])
                decoded_pkt_id = decoded_native_pkt.encoded_pkts[0].pkt_id
                decoded_native_pkt.local_pkt_seq_num = cope_pkt.local_pkt_seq_num
                decoded_native_pkt.checksum = crc_funcs.crc_checksum(str(decoded_native_pkt))
                decoded_native_pkt.payload = scapy.Raw(decoded_payload)
                
                # Debug
                # decoded_native_pkt.show2()
                decoded_packet_str = coding_utils.COPE_to_str(decoded_native_pkt)
                # self.logger.debug(decoded_packet_str)

                self.sharedState.addPacketToPacketPool(decoded_pkt_id, decoded_native_pkt)
                self.sharedState.incrementPacketsDecoded()
                # self.logger.info("Packets decoded: %d" % (self.sharedState.getPacketsDecoded()))

                self.enqueuer.enqueue(decoded_native_pkt)

            return True

def main():
    # Test setup - send one native packet and one encoded packet

    sharedState = SharedState()
    streamOrderer = StreamOrderer(sharedState)
    enqueuer = Enqueuer(sharedState, streamOrderer)
    decoder = Decoder(sharedState, enqueuer)

    src_ip1 = "10.0.0.1"
    src_ip2 = "10.0.0.2"
    dst_hwaddr = "00:00:00:00:00:03"
    from_neighbour = "00:00:00:00:00:02"
    cope_pkt = COPE_classes.COPE_packet()
    pkt_id_str = src_ip1+str(1)
    pkt_id1 = crc_funcs.crc_hash(pkt_id_str)
    cope_pkt.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id1, nexthop=dst_hwaddr))
    cope_pkt.local_pkt_seq_num = 1
    cope_pkt.checksum = crc_funcs.crc_checksum(str(cope_pkt))
    cope_pkt.payload = scapy.IP() / scapy.Raw("Hello")

    decoder.decode(cope_pkt, from_neighbour)

    cope_pkt = COPE_classes.COPE_packet()
    pkt_id_str = src_ip2+str(2)
    pkt_id2 = crc_funcs.crc_hash(pkt_id_str)
    cope_pkt.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id1, nexthop=dst_hwaddr))
    cope_pkt.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id2, nexthop=dst_hwaddr))
    cope_pkt.local_pkt_seq_num = 2
    cope_pkt.checksum = crc_funcs.crc_checksum(str(cope_pkt))
    cope_pkt.payload = scapy.IP() / scapy.Raw("\x00\x00\x00\x00\x01")

    decoder.decode(cope_pkt, from_neighbour)


if __name__ == '__main__':
    main()