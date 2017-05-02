import threading
import logging
import logging.config
import time

class ControlPktWaiter(threading.Thread):

    def __init__(self, sharedState):
        threading.Thread.__init__(self)
        self.sharedState = sharedState
        self.stop_event = threading.Event()
        self.startTime = time.time()
        self.daemon = True
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger('nc_node.ControlPktWaiter')


    def restartWaiter(self):
        pass


    def run(self):
        for i in range(self.sharedState.controlPktTimeout):
            self.stop_event.wait(self.sharedState.ack_retry_time)
            if self.stop_event.is_set():
                self.logger.debug("ACKWaiter was stopped")
                return
            else:
                self.logger.debug("Resending packet %s", self.pkt.local_pkt_seq_num)
                self.transmitter.transmit(self.pkt)

        self.sharedState.incrementFailedACKs()