import logging
logging.basicConfig(level=logging.DEBUG)

class StreamOrderer(object):

	def __init__(self, sharedState):
		self.sharedState = sharedState
		self.stream_list = list()
		logging.config.fileConfig('logging.conf')
		self.logger = logging.getLogger('nc_node.StreamOrderer')

	def order_stream(self, cope_packet):
		self.logger.debug("Got packet to order \n")
		self.stream_list.append(cope_packet)

		appInstance = self.sharedState.getAppInstance()

		if appInstance:
			appInstance.trafficOut(cope_packet)
			self.sharedState.incrementTrafficPktsOut()