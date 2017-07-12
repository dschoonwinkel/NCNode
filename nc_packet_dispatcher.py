import logging
import logging.config
import time
from pypacker.layer12 import cope
logging.config.fileConfig('logging.conf')

class PacketDispatcher(object):

    def __init__(self, sharedState, encoder):
        self.sharedState = sharedState
        self.encoder = encoder
        #self.#logger =logging.getLogger('nc_node.ncPacketDispatcher')

    def dispatch(self):

        if len(self.sharedState.output_queue_order) >= self.sharedState.getMinBufferLen():      # 500 ns
            #self.#logger.debug("Taking packet from the front of packet queue")
            dstMAC = self.sharedState.output_queue_order[0]                                     #102 ns
            out_pkt = self.sharedState.getHeadPacketFromQueues()                                # 15.5 ms   Hopefully faster now that a deque is used
            # out_pkt.show2()
            self.sharedState.times["Packet dispatcher send"].append(time.time())
            self.encoder.encode(out_pkt)
        else:
            #self.#logger.debug("Output queue is too short")
            return

    def dispatchControlPkt(self):
        #self.#logger.debug("dispatchControlPkt")
        # If ACKs and Receipts need to be dispatched
        if len(self.sharedState.ack_queue) > 0 or len(self.sharedState.receipts_queue) > 0:
            if len(self.sharedState.output_queue_order) >= self.sharedState.getMinBufferLen():
                self.dispatch()

            else: 
                cope_pkt = cope.COPE_packet()
                self.encoder.encode(cope_pkt)