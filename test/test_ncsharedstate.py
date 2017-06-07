import unittest
import nc_shared_state
import COPE_packet_classes as COPE_classes
from pypacker.layer12 import cope
from pypacker.layer3 import ip
import crc_funcs
import logging
import logging.config
logging.config.fileConfig('logging.conf')
#logger =logging.getLogger('nc_node.test_ncsharedstate')


class TestSharedState(unittest.TestCase):
    def test_scheduleACK(self):
        # #logger.debug("\n\n Testing scheduleACK()")
        sharedState = nc_shared_state.SharedState()
        neighbour = "00:00:00:01:00:00"
        seq_no = 1

        sharedState.scheduleACK(neighbour, seq_no)
        # sharedState.ack_queue[-1].show2()
        self.assertEqual(sharedState.ack_queue[-1].ack_map, 1)
        sharedState.scheduleACK(neighbour, seq_no + 1)
        # sharedState.ack_queue[-1].show2()
        self.assertEqual(sharedState.ack_queue[-1].ack_map, 3)
        sharedState.scheduleACK(neighbour, seq_no + 3)
        # sharedState.ack_queue[-1].show2()
        self.assertEqual(sharedState.ack_queue[-1].ack_map, 13)
        sharedState.scheduleACK(neighbour, seq_no + 4)
        # sharedState.ack_queue[-1].show2()
        self.assertEqual(sharedState.ack_queue[-1].ack_map, 27)

    def test_scheduleACK(self):
        # #logger.debug("\n\n Testing scheduleACK()")
        sharedState = nc_shared_state.SharedState()
        neighbour = "00:00:00:01:00:00"
        seq_no = 2

        sharedState.scheduleACK(neighbour, seq_no)
        #sharedState.ack_queue[-1].show2()
        self.assertEqual(sharedState.ack_queue[-1].ack_map, 1)
        sharedState.scheduleACK(neighbour, seq_no + 1)
        #sharedState.ack_queue[-1].show2()
        self.assertEqual(sharedState.ack_queue[-1].ack_map, 3)
        sharedState.scheduleACK(neighbour, seq_no + 3)
        #sharedState.ack_queue[-1].show2()
        self.assertEqual(sharedState.ack_queue[-1].ack_map, 13)
        sharedState.scheduleACK(neighbour, seq_no + 4)
        #sharedState.ack_queue[-1].show2()
        self.assertEqual(sharedState.ack_queue[-1].ack_map, 27)

        # Test reversed (resent packet) ordering
        sharedState.scheduleACK(neighbour, seq_no-1)
        #sharedState.ack_queue[-1].show2()
        self.assertEqual(sharedState.ack_queue[-1].ack_map, 59)

    def test_scheduleReceipts(self):
        # #logger.debug("\n\n Testing scheduleReceipts()")
        sharedState = nc_shared_state.SharedState()
        neighbour = "00:00:00:01:00:00"
        ip_seq_no = 1
        cope_pkt = cope.COPE_packet() + ip.IP(id=ip_seq_no, src_s="10.0.0.1")
        cope_pkt[ip.IP].body_bytes = b"Hello!"

        sharedState.scheduleReceipts(cope_pkt)
        # sharedState.receipts_queue[-1].show2()
        self.assertEqual(sharedState.receipts_queue[-1].bit_map, 1)
        cope_pkt[ip.IP].id = ip_seq_no + 1
        sharedState.scheduleReceipts(cope_pkt)
        # sharedState.receipts_queue[-1].show2()
        self.assertEqual(sharedState.receipts_queue[-1].bit_map, 3)
        cope_pkt[ip.IP].id = ip_seq_no + 3
        sharedState.scheduleReceipts(cope_pkt)
        # sharedState.receipts_queue[-1].show2()
        self.assertEqual(sharedState.receipts_queue[-1].bit_map, 13)
        cope_pkt[ip.IP].id = ip_seq_no + 4
        sharedState.scheduleReceipts(cope_pkt)
        # sharedState.receipts_queue[-1].show2()
        self.assertEqual(sharedState.receipts_queue[-1].bit_map, 27)

    # def test_updateRecpReports(self):
    #     sharedState = nc_shared_state.SharedState()
    #     report = COPE_classes.ReportHeader()
    #
    #     src_ip = "10.0.0.1"
    #     report.src_ip = src_ip
    #     report.last_pkt = 10
    #     report.bit_map = 138
    #
    #     sharedState.updateRecpReports(report)
    #
    #     self.assertFalse(11 in sharedState.neighbour_recp_rep["10.0.0.1"], '11 should not be in set')
    #     self.assertFalse(3 in sharedState.neighbour_recp_rep["10.0.0.1"], '3')
    #     self.assertFalse(7 in sharedState.neighbour_recp_rep["10.0.0.1"], '7')
    #     self.assertTrue(10 in sharedState.neighbour_recp_rep["10.0.0.1"], '10')
    #     self.assertTrue(8 in sharedState.neighbour_recp_rep["10.0.0.1"], '8')
    #     self.assertTrue(6 in sharedState.neighbour_recp_rep["10.0.0.1"], '6')
    #     self.assertTrue(2 in sharedState.neighbour_recp_rep["10.0.0.1"], '2')

    def test_getOutputQueueReady(self):
        sharedState = nc_shared_state.SharedState()

        dest_hw_addr = "00:00:00:00:00:02"

        cope_pkt = COPE_classes.COPE_packet() / "NC Runner test2"

        src_ip = sharedState.get_my_ip_addr()
        pkt_id_str = src_ip + str(1)
        pkt_id = crc_funcs.crc_hash(pkt_id_str)
        cope_pkt.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id, nexthop=dest_hw_addr))
        cope_pkt.local_pkt_seq_num = 1
        cope_pkt.calc_checksum()
        sharedState.addPacketToOutputQueue(dest_hw_addr, cope_pkt)

        queues_ready = sharedState.getOutputQueueReady(first_addr=dest_hw_addr)
        self.assertEqual(len(queues_ready), 0, "Queue lengths were not equal")

        queues_ready = sharedState.getOutputQueueReady()
        self.assertEqual(len(queues_ready), 1, "Queues length was too short")
        self.assertEqual(queues_ready[0], dest_hw_addr, "Incorrect address returned")

    def test_peekPacketFromQueue(self):
        sharedState = nc_shared_state.SharedState()

        dest_hw_addr = "00:00:00:00:00:02"

        cope_pkt1 = COPE_classes.COPE_packet() / "NC Runner test2"

        src_ip = sharedState.get_my_ip_addr()
        pkt_id_str = src_ip + str(1)
        pkt_id = crc_funcs.crc_hash(pkt_id_str)
        cope_pkt1.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id, nexthop=dest_hw_addr))
        cope_pkt1.local_pkt_seq_num = 1
        cope_pkt1.calc_checksum()
        sharedState.addPacketToOutputQueue(dest_hw_addr, cope_pkt1)

        cope_pkt2 = COPE_classes.COPE_packet() / "NC Runner test2"

        src_ip = sharedState.get_my_ip_addr()
        pkt_id_str = src_ip + str(2)
        pkt_id = crc_funcs.crc_hash(pkt_id_str)
        cope_pkt2.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id, nexthop=dest_hw_addr))
        cope_pkt2.local_pkt_seq_num = 2
        cope_pkt2.calc_checksum()
        sharedState.addPacketToOutputQueue(dest_hw_addr, cope_pkt2)

        first_pkt = sharedState.peekPacketFromQueue(dest_hw_addr)
        self.assertEqual(first_pkt, cope_pkt1, "Wrong packet at the front of the queue")

        first_pkt = sharedState.peekPacketFromQueue(dest_hw_addr)
        self.assertEqual(first_pkt, cope_pkt1, "Wrong packet at the front of the queue")

        self.assertEqual(len(sharedState.packet_queues[dest_hw_addr]), 2, "Incorrect queue length before dequeue")

        first_pkt = sharedState.getPacketFromQueue(dest_hw_addr)
        self.assertEqual(first_pkt, cope_pkt1, "Wrong packet at the front of the queue")

        self.assertEqual(len(sharedState.packet_queues[dest_hw_addr]), 1, "Incorrect queue length after dequeue")

        first_pkt = sharedState.peekPacketFromQueue(dest_hw_addr)
        self.assertEqual(first_pkt, cope_pkt2, "Wrong packet at the front of the queue")

        first_pkt = sharedState.getPacketFromQueue(dest_hw_addr)
        self.assertEqual(first_pkt, cope_pkt2, "Wrong packet at the front of the queue")

        self.assertEqual(len(sharedState.packet_queues[dest_hw_addr]), 0, "Incorrect queue length before dequeue")

    def test_getPacketFromQueue(self):
        sharedState = nc_shared_state.SharedState()

        dest_hw_addr = "00:00:00:00:00:02"

        cope_pkt1 = COPE_classes.COPE_packet() / "NC Runner test2"

        src_ip = sharedState.get_my_ip_addr()
        pkt_id_str = src_ip + str(1)
        pkt_id = crc_funcs.crc_hash(pkt_id_str)
        cope_pkt1.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id, nexthop=dest_hw_addr))
        cope_pkt1.local_pkt_seq_num = 1
        cope_pkt1.calc_checksum()
        sharedState.addPacketToOutputQueue(dest_hw_addr, cope_pkt1)

        pkt = sharedState.getPacketFromQueue(dest_hw_addr)

        self.assertEqual(pkt, cope_pkt1, "Incorrect pkt dequeued")
        self.assertEqual(len(sharedState.output_queue_order), 0, "Output queue len was not 0")

    def test_getHeadPacketOutputQueues(self):
        sharedState = nc_shared_state.SharedState()

        dest_hw_addr = "00:00:00:00:00:02"

        cope_pkt1 = COPE_classes.COPE_packet() / "NC Runner test2"

        src_ip = sharedState.get_my_ip_addr()
        pkt_id_str = src_ip + str(1)
        pkt_id = crc_funcs.crc_hash(pkt_id_str)
        cope_pkt1.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id, nexthop=dest_hw_addr))
        cope_pkt1.local_pkt_seq_num = 1
        cope_pkt1.calc_checksum()
        sharedState.addPacketToOutputQueue(dest_hw_addr, cope_pkt1)

        cope_pkt2 = COPE_classes.COPE_packet() / "NC Runner test2"

        src_ip = sharedState.get_my_ip_addr()
        pkt_id_str = src_ip + str(2)
        pkt_id = crc_funcs.crc_hash(pkt_id_str)
        cope_pkt2.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id, nexthop=dest_hw_addr))
        cope_pkt2.local_pkt_seq_num = 2
        cope_pkt2.calc_checksum()
        sharedState.addPacketToOutputQueue(dest_hw_addr, cope_pkt2)

        pkt = sharedState.getHeadPacketFromQueues()
        # pkt.show2()
        self.assertEqual(pkt, cope_pkt1, "Incorrect packet dequeued")

    def test_wasPktIdReceivedTrue(self):
        sharedState = nc_shared_state.SharedState()
        dest_hw_addr = "00:00:00:00:00:02"

        src_ip = sharedState.get_my_ip_addr()
        pkt_id_str = src_ip + str(1)
        pkt_id = crc_funcs.crc_hash(pkt_id_str)
        cope_pkt1 = COPE_classes.COPE_packet() / "NC Runner test2"
        cope_pkt1.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id, nexthop=dest_hw_addr))

        sharedState.addPacketToPacketPool(pkt_id, cope_pkt1)
        self.assertTrue(sharedState.wasPktIdReceived(pkt_id))

    def test_wasPktIdReceivedFalse(self):
        sharedState = nc_shared_state.SharedState()
        dest_hw_addr = "00:00:00:00:00:02"

        src_ip = sharedState.get_my_ip_addr()
        pkt_id_str = src_ip + str(1)
        pkt_id = crc_funcs.crc_hash(pkt_id_str)
        cope_pkt1 = COPE_classes.COPE_packet() / "NC Runner test2"
        cope_pkt1.encoded_pkts.append(COPE_classes.EncodedHeader(pkt_id=pkt_id, nexthop=dest_hw_addr))

        self.assertFalse(sharedState.wasPktIdReceived(pkt_id))



def main():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSharedState)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #logger.debug("Tests run")


if __name__ == '__main__':
    main()
