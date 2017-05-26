import logging
# logging.basicConfig(level=logging.DEBUG)
import scapy.all as scapy
import COPE_packet_classes as COPE_classes
import logging.config
import crc_funcs
import time


class Transmitter(object):

	def __init__(self, sharedState):
		self.sharedState = sharedState
		self.broadcast_HWAddr = "ff:ff:ff:ff:ff:ff"
		logging.config.fileConfig('logging.conf')
		#self.#logger =logging.getLogger('nc_node.Transmitter')

	def transmit(self, pkt):
		networkInstance = self.sharedState.getNetworkInstance()

		# pkt.show2()

		if networkInstance:
			#self.#logger.debug("Transmitting packet\n")

			# Calculate final checksum here
			pkt.calc_checksum()
			encap_pkt = None
			# #logger.debug(Encoded num", pkt.ENCODED_NUM

			# Do packet encapsulation here...
			# #self.#logger.debug("my hw addr: %s" % self.sharedState.get_my_hw_addr())
			if len(pkt.encoded_pkts) == 0:
				encap_pkt = scapy.Ether(src=self.sharedState.get_my_hw_addr(), dst=self.broadcast_HWAddr, type=COPE_classes.COPE_PACKET_TYPE)/pkt
			elif len(pkt.encoded_pkts) == 1:
				encap_pkt = scapy.Ether(src=self.sharedState.get_my_hw_addr(), dst=pkt.encoded_pkts[0].nexthop, type=COPE_classes.COPE_PACKET_TYPE)/pkt
				self.sharedState.incrementPktsSent(encoded = False)
			elif len(pkt.encoded_pkts) > 1:
				encap_pkt = scapy.Ether(src=self.sharedState.get_my_hw_addr(), dst=self.broadcast_HWAddr, type=COPE_classes.COPE_PACKET_TYPE)/pkt
				self.sharedState.incrementPktsSent(encoded = True)
			else:
				#self.#logger.error("Impossible ENCODED_NUM, stopping transmit")
				return

			# encap_pkt.show2()

			self.sharedState.resetControlPktScheduler()
			self.sharedState.times["Transmitter send"].append(time.time())
			networkInstance.sendPkt(encap_pkt)
				
		else:
			#self.#logger.debug("Network Instance was null, not transmitting\n")
			pass

	def dropPkt(self, pkt_id):
		networkInstance = self.sharedState.getNetworkInstance()

		if networkInstance:
			#self.#logger.debug("Dropping packet %d", pkt_id)
			networkInstance.dropPkt(pkt_id)