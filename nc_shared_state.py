#Imports
from sets import Set
from collections import deque
import threading
import logging
import logging.config
import COPE_packet_classes as COPE_classes
import scapy.all as scapy
import network_utils
import nc_scheduler
import network_utils

class SharedState(object):

    def __init__(self):

        #Network state
        self.my_ip_addr = "0.0.0.0"
        # self.my_hw_addr = "00:00:00:00:00:00"
        # self.my_hw_addr = network_utils.get_HWAddr("eth1")
        self.my_hw_addr = network_utils.get_first_HWAddr()
        self.my_nic_name = network_utils.get_first_NicName()
        self.ack_retries = 2                         # number of retries before ACK waiter thread stops retransmitting
        self.controlPktTimeout = 4                   # Timeout to wait for before acks and reports are sent as control packets
        self.controlWaiterCheckInterval = 2              # Check interval for the Control Waiter
        self.ack_retry_time = 30
        self.mac_to_port = dict()                    # dict(mac_addr, int) -- switch port on which to send out on, i.e. routing
        self.ip_to_mac = dict()                      # dict(IP, mac_addr) -- which MAC addr is closest to this IP, implicitly, which port should it be sent on. Used for routing
        self.ip_to_port = dict()                     # dict(IP, int) -- switch port on which to send out on, i.e. routing
        self.pktid_to_buffer_id = dict()             # dict(pkt_id, int) -- maps COPE pkt_id to buffer_id. Used for dropping packets that should not be sent
        self.run_event = threading.Event()
        self.run_event.set()

        #Interaction instances
        self.appInstance = None                        # Application instance (container) as traffic sink
        self.networkInstance = None                    # Network instance (container) as packet sender, and for drop command
        self.networkSocket = None

        #Packet output queues
        self.packet_queues = dict()                   # dict(dstMAC, Deque)
        self.output_queue_order = list()              # list of dstMACs to keep order of stream correct
        self.ack_queue = list()                       # ACKs scheduled for transmission
        self.ack_history = dict()                     # dict(MAC, byte) ACK report cumulative history
        self.receipts_queue = list()                  # Receipt reports scheduled for distribution        
        self.receipts_history = dict()                # dict(SRC_IP, byte) Reception reports cumulative history

        #Packet pool, recv set, application queue
        self.packet_pool = dict()                     # dict(pkt_id, cope_pkt)
        self.packet_ids_recv = Set()                  # Set(pkt_ids)
        self.app_queue = deque                # Queue (cope_pkts) -- received and ordered packets ready to be dispatched to app layer

        # Neighbour state
        self.neighbour_seqnr_sent = dict()                # dict(MAC, int)
        self.neighbour_seqnr_recv = dict()                # dict(MAC, int)
        self.neighbour_recp_rep = dict()             # dict(IP, Set())
        self.neighbour_recvd = dict()                 # dict(MAC, Set())
        self.ack_waiters = dict()                    # dict(tuple(neighbour, ack_id), ACKWaiterThread)    -- ACK waiter threads for each sent packet
        self.controlPktWaiter = nc_scheduler.ControlPktWaiter(self)

        #Statistics + Counters
        self.packet_count_recv = 0
        self.packet_count_seen = 0
        self.native_packets_sent = 0
        self.encoded_packets_sent = 0
        
        self.packets_decoded = 0
        self.acks_failed = 0
        
        self.traffic_packets_in = 0
        self.traffic_packets_out = 0

        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('nc_node.ncSharedState')

    def get_my_ip_addr(self):
        return self.my_ip_addr

    def get_my_hw_addr(self):
        return self.my_hw_addr

    def get_my_NicName(self):
        return self.my_nic_name

    def get_neighbour_seqnr_sent(self, hw_addr):
        return self.neighbour_seqnr_sent[hw_addr]

    def incrementNeighbourSeqnoSent(self, neighbour, number = 1):
        if neighbour not in self.neighbour_seqnr_sent:
            self.neighbour_seqnr_sent[neighbour] = 0

        self.neighbour_seqnr_sent[neighbour] += number
        logging.debug("incrementNeighbourSeqnoSent for neighbour %s" % neighbour)

    def incrementNeighbourSeqnoRecv(self, neighbour, number = 1):
        self.neighbour_seqnr_recv[neighbour] += number
        logging.debug("incrementNeighbourSeqnoRecv for neighbour %s" % neighbour)

    def get_neighbour_recp_rep(self, ip_addr):
        return self.neighbour_recp_rep[ip_addr]

    def hasNeighbourReceived(self, neighbour, pkt_id):
        # If we have never heard from the neighbour, we don't know if it has the packet
        if neighbour not in self.neighbour_recvd:
            return False
        # Check if the pkt_id is in the neighbour received set
        return pkt_id in self.neighbour_recvd[neighbour]

    def wasPktIdReceived(self, pkt_id):
        return pkt_id in self.packet_ids_recv

    def addACK_waiter(self, neighbour, ack_id, waiter):
        self.ack_waiters[(neighbour, ack_id)] = waiter
        # print self.ack_waiters.keys()

    def updateRecpReports(self, report):
        if report.src_ip not in self.neighbour_recp_rep:
            # Create reception report set for each neighbour
            self.neighbour_recp_rep[report.src_ip] = Set()

        # Put the last_pkt number into the received reports for that neighbour
        self.neighbour_recp_rep[report.src_ip].add(report.last_pkt)

        for i in range(1, 8):
            if (report.bit_map >> i & 1):
                # print bin(report.bit_map)
                # print i, report.last_pkt - i - 1
                self.neighbour_recp_rep[report.src_ip].add(report.last_pkt - i - 1)

    def updateACKwaiters(self, ackreport, neighbour):
        self.logger.debug("Ackreport " + str(ackreport))
        if str(ackreport.neighbour) is self.my_hw_addr:
            # self.logger.debug("updateACKwaiters running")
            if (neighbour, ackreport.last_ack) in self.ack_waiters:

                # Add a neighbour recvd set if there none for this neighbour
                if neighbour not in self.neighbour_recvd:
                    self.neighbour_recvd[neighbour] = Set()

                # Pop removes and returns reference
                ack_waiter = self.ack_waiters.pop((neighbour, ackreport.last_ack))

                # Use the ack_waiter information to put the correct pkt_id in the neighbour recvd set
                self.neighbour_recvd[neighbour].add(ack_waiter.pkt.get_pktid(neighbour))
                # Stop the ACKwaiter
                ack_waiter.stopWaiter()

                
            for i in range(1, 8):
                if (ackreport.ack_map >> i & 1):
                    # self.logger.debug("updateACKwaiters stopping %d" % (ackreport.last_ack - i - 1))
                    # print bin(report.ack_map)
                    # print i, report.last_pkt - i - 1
                    if (neighbour, ackreport.last_ack - i - 1) in self.ack_waiters:
                        # Pop removes and returns reference
                        self.logger.debug("removing " + str((neighbour, ackreport.last_ack - i - 1)) + " from ackwaiters")

                        ack_waiter = self.ack_waiters.pop((neighbour, ackreport.last_ack - i - 1))
                        self.neighbour_recvd[neighbour].add(ack_waiter.pkt.get_pktid(neighbour))
                        ack_waiter.stopWaiter()

    def setNetworkSocket(self, socket):
        self.networkSocket = socket

    def getNetworkSocket(self):
        return self.networkSocket

    def setRunEvent(self):
        self.run_event.set()

    def clearRunEvent(self):
        self.run_event.clear()

    def addPacketToPacketPool(self, pkt_id, cope_pkt):
        self.packet_pool[pkt_id] = cope_pkt
        self.packet_ids_recv.add(pkt_id)
        
    def addPacketToOutputQueue(self, dstMAC, cope_pkt):
        if dstMAC not in self.packet_queues:
            # self.logger.debug("Adding new neighbour output queue")
            q = deque()
            q.append(cope_pkt)
            self.packet_queues[dstMAC] = q

        elif dstMAC in self.packet_queues:
            # self.logger.debug("Adding packet to existing neighbour output queue")
            q = self.packet_queues[dstMAC]
            q.append(cope_pkt)

        self.output_queue_order.append(dstMAC)

    def getPacketFromPacketPool(self, pkt_id):
        return self.packet_pool[pkt_id]

    def getHeadPacketFromQueues(self):
        # Get the packet received first, i.e. at the front of the output_queue_order
        return self.getPacketFromQueue(self.output_queue_order[0])

    def peekPacketFromQueue(self, queue_key):
        # Look at, but not dequeue the packet at the head of the queue
        return self.packet_queues[queue_key][0]

    def getPacketFromQueue(self, queue_key):
        # Also remember to dequeue from output queue order here
        self.output_queue_order.remove(queue_key)

        # Pop left removes from front of the queue
        return self.packet_queues[queue_key].popleft()

    def getOutputQueueReady(self, first_addr = ""):
        # Queue length check will only be done once a valid COPE packet
        # is received -- consider revising this later
        packet_queues_ready = list()

        # #######################
        # This is not order safe
        # #######################

        for key in self.packet_queues.keys():
            # Ensure that only different destinations are coded together
            if key not in packet_queues_ready and key != first_addr:
                packet_queues_ready.append(key)

        return packet_queues_ready

    def getOutputQueueLen(self):
        return len(self.output_queue_order)


    def incrementPacketRecv(self, packets = 1):
        self.packet_count_recv += packets
        logging.debug("incrementPacketRecv: %d" % self.packet_count_recv)

    def incrementPacketSeen(self, packets = 1):
        self.packet_count_seen += packets
        logging.debug("incrementPacketRecv: %d" % self.packet_count_seen)

    def incrementTrafficPktsIn(self, packets = 1):
        self.traffic_packets_in += packets
        logging.debug("incrementTrafficPktsIn: %d" % self.traffic_packets_in)

    def incrementTrafficPktsOut(self, packets = 1):
        self.traffic_packets_out += packets
        logging.debug("incrementTrafficPktsOut: %d" % self.traffic_packets_out)

    def incrementPktsSent(self, packets = 1, encoded = False):
        if not encoded:
            self.native_packets_sent += packets
            logging.debug("incrementNativePktsSent: %d" % self.native_packets_sent)
        else:
            self.encoded_packets_sent += packets
            logging.debug("incrementEncodedPktsSent: %d" % self.encoded_packets_sent)
    
    def incrementFailedACKs(self, failed = 1):
        self.acks_failed += failed
        logging.debug("incrementFailedACKs: %d" % self.acks_failed)    

    def getPacketRecv(self):
        return self.packet_count_recv

    def getPacketSeen(self):
        return self.packet_count_seen

    def incrementPacketsDecoded(self):
        self.packets_decoded += 1

    def getPacketsDecoded(self):
        return self.packets_decoded

    def getAppInstance(self):
        return self.appInstance
       
    def getNetworkInstance(self):
        return self.networkInstance

    def scheduleACK(self, neighbour, seq_no):
        logging.debug("scheduling ACK for seq_no %d" % seq_no)
        ack_header = COPE_classes.ACKHeader()
        ack_header.neighbour = neighbour
        ack_header.last_ack = seq_no

        if neighbour in self.ack_history:
            ackmap = self.ack_history[neighbour]
        else:
            ackmap = 0

        # Shift the old ackmap completely out of the map by default
        seq_no_difference = 8

        # Find the correct seqno distance, if not default
        for ack in reversed(self.ack_queue):
            if ack.neighbour == neighbour:
                seq_no_difference = seq_no - ack.last_ack
                break

        # Shift the ackmap by the difference in seq_no
        ackmap = (ackmap << seq_no_difference | 1) & 255

        self.ack_history[neighbour] = ackmap
        ack_header.ack_map = ackmap

        self.ack_queue.append(ack_header)

    def scheduleReceipts(self, cope_pkt):
        receipt_header = COPE_classes.ReportHeader()

        ip_pkt = network_utils.check_IPPacket(cope_pkt.payload)

        # If the payload does not contain an IP packet, receipt reports can not be scheduled
        if ip_pkt:
            # BEWARE!! This assumes that ip ID field are set up beforehand to be sequential. Could change
            # as the packet moves across the network, but should be fine for subnets
            src_ip = ip_pkt.src
            ip_seq_no = ip_pkt.id
            receipt_header.src_ip = src_ip
            receipt_header.last_pkt = ip_seq_no

            logging.debug("scheduling Receipts for ip_seq_no %d" % ip_seq_no)

            if ip_pkt.src in self.receipts_history:
                bit_map = self.receipts_history[src_ip]
            else:
                bit_map = 0

            # Shift the old bitmap completely out of the map by default
            seq_no_difference = 8

            # Find the correct seqno distance, if not default
            for report in reversed(self.receipts_queue):
                if report.src_ip == src_ip:
                    seq_no_difference = ip_seq_no - report.last_pkt
                    break

            # Shift the ackmap by the difference in seq_no
            bit_map = (bit_map << seq_no_difference | 1) & 255

            self.receipts_history[src_ip] = bit_map
            receipt_header.bit_map = bit_map

            self.receipts_queue.append(receipt_header)

    def stopACKWaiters(self):
        print self.ack_waiters.keys()
        for key in list(self.ack_waiters.keys()):
            # print key
            self.ack_waiters[key].stopWaiter()

def main():
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('nc_node.ncSharedStateMain')
    logger.debug("Everything is working")

if __name__ == '__main__':
    main()