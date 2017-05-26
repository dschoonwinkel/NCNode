import unittest
import mock
import nc_shared_state
import nc_packet_dispatcher
import COPE_packet_classes as COPE_classes
import scapy.all as scapy
import logging
import logging.config
logging.config.fileConfig('logging.conf')
#logger =logging.getLogger('nc_node.test_ncpacketdispatcher')

class TestPacketDispatcher(unittest.TestCase):

	def test_dispatch(self):
		sharedState = nc_shared_state.SharedState()
		cope_pkt = COPE_classes.COPE_packet()
		
		sharedState.addPacketToOutputQueue("00:00:00:00:00:01", cope_pkt)
		sharedState.min_buffer_len = 2

		mockEncoder = mock.Mock()
		packetDispatcher = nc_packet_dispatcher.PacketDispatcher(sharedState, mockEncoder)
		packetDispatcher.dispatch()

		# If Encoder.encode was called prematurely
		mockEncoder.encode.assert_not_called()

		# Dispatcher requires at least 2 packet in output queue, otherwise it will 
		# wait for another packet
		sharedState.addPacketToOutputQueue("00:00:00:00:00:01", cope_pkt)
		packetDispatcher.dispatch()
		mockEncoder.encode.assert_called_with(cope_pkt)
		
	def test_not_dispatch(self):
		sharedState = nc_shared_state.SharedState()
		
		mockEncoder = mock.Mock()

		packetDispatcher = nc_packet_dispatcher.PacketDispatcher(sharedState, mockEncoder)
		packetDispatcher.dispatch()

		mockEncoder.encode.assert_not_called()

def main():
	suite = unittest.TestLoader().loadTestsFromTestCase(TestPacketDispatcher)
	unittest.TextTestRunner(verbosity=2).run(suite)
	#logger.debug("Tests run")

if __name__ == '__main__':
	main()