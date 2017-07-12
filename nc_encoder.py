import logging
import logging.config
import coding_utils
from pypacker.layer12 import cope
import time
# import COPE_packet_classes as COPE_classes
logging.config.fileConfig('logging.conf')

class Encoder(object):

    def __init__(self, sharedState, addAckRecps):
        self.sharedState = sharedState
        self.addACksRecps = addAckRecps

        #self.#logger =logging.getLogger('nc_node.Encoder')

    def encode(self, pkt):
        # Perform encoding functions here, or dispatch native packet
        #self.#logger.debug("Encoding packet")
        # pkt.show2()

        # Check if there are enough packets to code together, otherwise send uncoded
        # Assure that packet with the same nexthop destination is not coded together
        #self.#logger.debug("Encoded num %d" %len(pkt.encoded_pkts))

        if len(pkt.encoded_pkts) >= 1:                                                      # TODO 2.65
            packet_queues_ready = self.sharedState.getOutputQueueReady(first_addr=pkt.encoded_pkts[0].nexthop_s)      #TODO 6.5 us
        else:
            packet_queues_ready = self.sharedState.getOutputQueueReady()                    #TODO 860 ns

        #self.#logger.debug("Packet queues ready: %s" % str(packet_queues_ready))


        # If there is at least 1 packet to code together
        if packet_queues_ready and len(packet_queues_ready) >= 1:
            #self.#logger.debug("Starting coding process")

            # Get all the codeable packets in a list
            cope_pkts = list()
            # First packet in the list should be the packet that we want to send. Include only 
            # if there is 
            if len(pkt.encoded_pkts) >= 1:
                cope_pkts.append(pkt)

            print(cope_pkts)

            for i in range(len(packet_queues_ready)):
                if self.sharedState.peekPacketFromQueue(packet_queues_ready[i]):
                    cope_pkts.append(self.sharedState.peekPacketFromQueue(packet_queues_ready[i]))

            valid_codables, rest_pkts = self.findCodables(cope_pkts)

            # Create a new encoded packet, starting with original packet
            coded_pkt = cope.COPE_packet()
            coded_payload = b''

            #self.#logger.debug("Len of valid_codables %d" % len(valid_codables))

            # There are packets to encode
            if valid_codables and len(valid_codables) >= 1:
                # Encode additional packet together, if they are decodable at the receiver
                for cope_pkt in valid_codables:
                    coded_pkt.encoded_pkts.append(cope_pkt.encoded_pkts[0])
                    coded_payload = coding_utils.bytexor(coded_payload, cope_pkt.body_bytes)

            # If the packet cannot be coded with any other packet
            else:
                if len(pkt.encoded_pkts) > 0:
                    coded_pkt.encoded_pkts.append(pkt.encoded_pkts[0])
                    coded_payload = pkt.body_bytes

            # #logger.debug(Output queue", output_queue
            coded_pkt.body_bytes = coded_payload

            self.sharedState.times["Encoder processed"].append(time.time())
            self.addACksRecps.addACKsRecps(coded_pkt)

        # Else: if output queue is long enough send uncoded immediately
        else:
            self.sharedState.times["Encoder processed"].append(time.time())
            self.addACksRecps.addACKsRecps(pkt)

    def findCodables(self, cope_pkts_list):

        # Create sets for each node's possibilities
        possiblities_sets = dict()

        print(cope_pkts_list)

        # For each packet header a
        for neighbour_a in cope_pkts_list:
            print("Hello!")
            possiblities_sets[neighbour_a.encoded_pkts[0].nexthop_s] = set()
            # Add packet a, which we want to decode
            possiblities_sets[neighbour_a.encoded_pkts[0].nexthop_s].add(neighbour_a)

            # For each other packet header b
            for cope_pkt_b in cope_pkts_list:
                # Does a.neighbour.recvset not contain b.pkt_id
                if self.sharedState.hasNeighbourReceived(neighbour_a.encoded_pkts[0].nexthop_s,
                                                             cope_pkt_b.encoded_pkts[0].pkt_id):
                    # If so, add to possibilities set for a
                    possiblities_sets[neighbour_a.encoded_pkts[0].nexthop_s].add(cope_pkt_b)

        # for key in possiblities_sets.keys():
        #     print "\n\n\n\n\n\n neighbour %s" % key
        #     for pkt in possiblities_sets[key]:
        #         pkt.show2()

        valid_list = None
        remainder_list = None

        if possiblities_sets:
            valid_codables = set.intersection(*possiblities_sets.values())
            union_set = set.union(*possiblities_sets.values())
            remainder_pkts = set.difference(valid_codables, union_set)
            valid_list = list(valid_codables)
            remainder_list = list(remainder_pkts)

        return valid_list, remainder_list




    def dropPkt(self, pkt_id):
        #self.#logger.debug("Dropping packet id %d" % pkt_id)
        # Perform dropping of packets here, using transmitter module. May be necessary when
        # networkInstance is
        self.addACksRecps.dropPkt()