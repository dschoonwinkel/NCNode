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
        #self.#logger =logging.getLogger('nc_node.ControlPktWaiter')


    def restartWaiter(self):
        # Set the start_time = current_time to indicate that the waiting is reset, not timed out
        self.startTime = time.time()
        # Set wait event, so that wait loop can be restarted
        self.stop_event.set()
        pass


    def run(self):
        #self.#logger.debug("Starting ControlPktWaiter")
        self.startTime = time.time()
        # Loop while NCNode is running
        while self.sharedState.run_event.is_set():
            # #self.#logger.debug("ControlPktWaiter loop")

            # Wait until timeout or interruption
            self.stop_event.wait(self.sharedState.getControlPktTimeout())
            currentTime = time.time()
            # If it was the timeout, i.e. current_time > start_time + waittime, send control Pkt


            if currentTime > self.startTime + self.sharedState.getControlPktTimeout():
                # #self.#logger.debug("Timeout has occured")
                if len(self.sharedState.ack_queue) > 0 or len(self.sharedState.receipts_queue) > 0:
                    #self.#logger.debug("Sending control pkt")
                    self.sharedState.packetDispatcher.dispatchControlPkt()
            # Else if it was stopped or restarted, do nothing, the loop will restart waiting

            self.startTime = currentTime
            # Unset the stop_event to restart the waiting in the next loop
            self.stop_event.clear()