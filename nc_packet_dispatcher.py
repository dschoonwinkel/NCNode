import logging
import logging.config
import COPE_packet_classes as COPE_classes

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

    def dispatchControlPkt(self):
        self.logger.debug("dispatchControlPkt")

        if len(self.sharedState.output_queue_order) >= self.sharedState.getMinBufferLen():
            self.dispatch()

        else:
            cope_pkt = COPE_classes.COPE_packet()
            self.encoder.encode(cope_pkt)