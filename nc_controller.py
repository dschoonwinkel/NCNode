# Copyright 2012 James McCauley
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This component is for use with the OpenFlow tutorial.

It acts as a simple hub, but can be modified to act like an L2
learning switch.

It's roughly similar to the one Brandon Heller did for NOX.
"""

from pox.core import core
from pox.lib.addresses import EthAddr
from pox.lib.revent import EventRemove
from pox.lib.packet import ethernet
import pox.openflow.libopenflow_01 as of
import Queue
from scapy.all import *
from calculate_checksum import *
from coding_utils import *
from COPE_packet_classes import *
import logging
import datetime

log = core.getLogger()

output_queue = list()
packet_queues = dict()
packet_receipt_reports = dict()

COPE_packet_received_count = 0
COPE_packet_sent_native_count = 0
COPE_packet_sent_encoded_count = 0


class Tutorial(object):
    """
    A Tutorial object is created for each switch that connects.
    A Connection object for that switch is passed to the __init__ function.
    """

    def __init__(self, connection):
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)

        # Use this table to keep track of which ethernet address is on
        # which switch port (keys are MACs, values are ports).
        self.mac_to_port = {}

    def resend_packet(self, packet_in, out_port):
        """
        Instructs the switch to resend a packet that it had sent to us.
        "packet_in" is the ofp_packet_in object the switch had sent to the
        controller due to a table-miss.
        """
        msg = of.ofp_packet_out()
        msg.data = packet_in

        # Add an action to send to the specified port
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)

        # Send message to switch
        self.connection.send(msg)

    def drop_packet(self, packet_in, out_port):
        if packet_in.buffer_id is not None:
            # Kill the buffer
            log.debug("Buffer id %d" % packet_in.buffer_id)
            msg = of.ofp_packet_out(buffer_id=packet_in.buffer_id)
            self.connection.send(msg)

    def send_packet_out(self, packet_in, out_port):
        # For packet created at the controller
        msg = of.ofp_packet_out(in_port=of.OFPP_NONE)
        msg.data = packet_in

        # Add an action to send to the specified port
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)

        # Send message to switch
        self.connection.send(msg)

    def act_like_hub(self, packet, packet_in):
        self.resend_packet(packet_in, of.OFPP_ALL)

    def act_like_dropping_controller(self, packet, packet_in):
        self.drop_packet(packet_in, of.OFPP_NONE)
        ether_carrier = ethernet()
        ether_carrier.dst = EthAddr(b"\xff\xff\xff\xff\xff\xff")
        ether_carrier.type = COPE_PACKET_TYPE
        ether_carrier.payload = str("Hello")
        msg = of.ofp_packet_out(in_port=of.OFPP_NONE)
        msg.actions.append(of.ofp_action_output(port=of.OFPP_ALL))
        msg.data = ether_carrier
        log.debug("Sending new packet")
        self.connection.send(msg)

    def act_like_coding_controller(self, packet, packet_in):
        global packet_queues, COPE_packet_received_count, COPE_packet_sent_native_count, COPE_packet_sent_encoded_count
        # print packet

        raw_bytes = packet.pack()
        log.debug("Raw bytes" + str(raw_bytes))
        scapy_pkt = Ether(raw_bytes)

        arp = packet.find('arp')
        if arp is not None:
            log.info("Flooding ARP packet")
            self.resend_packet(packet_in, of.OFPP_ALL)
            return

        ping = packet.find('icmp')
        if ping is not None:
            log.info("Flooding ICMP packet")
            self.resend_packet(packet_in, of.OFPP_ALL)
            return

        if scapy_pkt.type == COPE_PACKET_TYPE:
            # #logger.debug(Possibly a cope packet"
            # print_hex("Raw bytes", raw_bytes)

            cope_pkt, cope_payload = extr_COPE_pkt(packet.payload)
            # print_hex("Cope packet: ", cope_pkt)

            if cope_pkt:
                COPE_packet_received_count += 1
                log.info("COPE_packets received: " + str(COPE_packet_received_count))

            # Native packet
            #logger.debug("Encoded NUM %d" % len(cope_pkt.encoded_pkts))
            if cope_pkt and len(cope_pkt.encoded_pkts) == 1:

                dstip = cope_pkt.encoded_pkts[0].nexthop
                if dstip not in packet_queues:
                    # #logger.debug(Adding new neighbour output queue"
                    q = Queue.Queue()
                    q.put(packet)
                    packet_queues[dstip] = q

                elif dstip in packet_queues:
                    # #logger.debug(Adding packet to existing neighbour output queue"
                    q = packet_queues[dstip]
                    q.put(packet)

                output_queue.append(dstip)

                # Queue length check will only be done once a valid COPE packet
                # is received -- consider revising this later
                packet_queues_ready = list()
                for key in output_queue:
                    # Ensure that only different destinations are coded together
                    if key not in packet_queues_ready:
                        packet_queues_ready.append(key)

                # #logger.debug(Packet queues ready", packet_queues_ready
                # #logger.debug(Output queue", output_queue

                # #logger.debug(Packet queues ready len", len(packet_queues_ready)
                # #logger.debug(Output queue len", len(output_queue)

                if len(packet_queues_ready) >= 2 and len(output_queue) >= 2:
                    log.info("Starting coding process")

                    pkt1 = packet_queues[packet_queues_ready[0]].get()
                    cope_pkt1, cope_payload1 = extr_COPE_pkt(pkt1.payload)

                    pkt2 = packet_queues[packet_queues_ready[1]].get()
                    cope_pkt2, cope_payload2 = extr_COPE_pkt(pkt2.payload)

                    output_queue.remove(packet_queues_ready[0])
                    output_queue.remove(packet_queues_ready[1])

                    coded_pkt = COPE_packet()

                    coded_pkt.encoded_pkts.append(cope_pkt1.encoded_pkts[0])
                    coded_pkt.encoded_pkts.append(cope_pkt2.encoded_pkts[0])
                    # #logger.debug(Packet 1 payload", ' '.join('%02X' % ord(x) for x in str(cope_payload1))
                    # #logger.debug(Packet 2 payload", ' '.join('%02X' % ord(x) for x in str(cope_payload2))
                    coded_payload = strxor(cope_payload1, cope_payload2)
                    # #logger.debug(Xor'ed payload", ' '.join('%02X' % ord(x) for x in str(coded_payload))

                    # #logger.debug(Output queue", output_queue
                    coded_pkt.checksum = crc_checksum(str(coded_pkt))
                    coded_pkt.payload = Raw(coded_payload)

                    # #logger.debug(Type of coded_pkt", type(coded_pkt)
                    # coded_pkt.show2()


                    # Drop the incoming packet, replaced by COPE coded packet
                    log.debug("Dropping packet (hopefully)")
                    self.drop_packet(packet_in, of.OFPP_NONE)
                    ether_carrier = ethernet()
                    ether_carrier.dst = "\xff\xff\xff\xff\xff\xff"
                    ether_carrier.type = COPE_PACKET_TYPE
                    ether_carrier.payload = str(coded_pkt)
                    msg = of.ofp_packet_out(in_port=of.OFPP_NONE)
                    msg.actions.append(of.ofp_action_output(port=of.OFPP_ALL))
                    msg.data = ether_carrier
                    log.debug("Sending new packet")
                    self.connection.send(msg)

                    COPE_packet_sent_encoded_count += 1
                    log.info("Sending encoded packet, count: " + str(COPE_packet_sent_encoded_count))

                    # else:
                    # Do some cleverer routing here eventually
                    # COPE_packet_sent_native_count += 1
                    # #logger.debug(Sending native packet id %d, count %d \n" % (cope_pkt.encoded_pkts[0].pkt_id,COPE_packet_sent_native_count)
                    # self.resend_packet(packet_in, of.OFPP_ALL)

    def _handle_PacketIn(self, event):
        """
        Handles packet in messages from the switch.
        """

        packet = event.parsed  # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp  # The actual ofp_packet_in message.

        # Comment out the following line and uncomment the one after
        # when starting the exercise.
        self.act_like_coding_controller(packet, packet_in)
        # self.act_like_dropping_controller(packet, packet_in)
        # self.act_like_hub(packet, packet_in)


def launch():
    """
    Starts the component
    """

    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        log.info("Starting log: " + st)

        Tutorial(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)

    # Request full packet miss payloads
    def set_miss_length(event=None):
        if not core.hasComponent('openflow'):
            return
        core.openflow.miss_send_len = 0x7fff
        core.getLogger().info("Requesting full packet payloads")
        return EventRemove

    if set_miss_length() is None:
        core.addListenerByName("ComponentRegistered", set_miss_length)