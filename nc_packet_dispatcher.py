import logging
import logging.config

class PacketDispatcher(object):

	def __init__(self, sharedState, encoder):
		self.sharedState = sharedState
		self.encoder = encoder
		logging.config.fileConfig('logging.conf')
		self.logger = logging.getLogger('nc_node.ncPacketDispatcher')

	def dispatch(self):
		
		if len(self.sharedState.output_queue_order) >= self.sharedState.getMinBufferLen():
			self.logger.debug("Taking packet from the front of packet queue")
			dstMAC = self.sharedState.output_queue_order[0]
			out_pkt = self.sharedState.getHeadPacketFromQueues()
			# out_pkt.show2()
			self.encoder.encode(out_pkt)
		else:
			self.logger.debug("Output queue is too short")
			return