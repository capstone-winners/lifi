
# States
# 0 - warm_up
# 1 - detected
# 2 - processing
# 
# [g r r b b b b g g g g r r r r g g g r b b b b g g g g]
#  0 0 0 1 1 1 1 2 2 2 2 2 2 2 2 2 2 2 2 1 1 1 1 2 2 2 2
#    -       -      0       1       0
# 
# on processing -> detected: trigger callback

from Lifi.CvHelpers import argmax, bin_list_to_int


class HistoryInterpreter():
    WARMUP = 0
    DETECTED = 1
    PROCESSING = 2

    def __init__(self):
        self.sentinel_value = "blue"
        self.low_value = "green"
        self.high_value = "red"

        self.state = HistoryInterpreter.WARMUP
        self.buffer = []
        self.max_buffer_size = 4

        self.output = []
        self.frame_complete_callback = self._frame_complete

    def process_batch(self, history):
        for entry in history:
            self.process(entry)

    def process(self, entry):
        if self.state == HistoryInterpreter.WARMUP:
            self._handle_warmup(entry)
        elif self.state == HistoryInterpreter.DETECTED:
            self._handle_detected(entry)
        elif self.state == HistoryInterpreter.PROCESSING:
            self._handle_processing(entry)

    def pop_output(self):
        temp = self.output
        self.output = []
        return temp

    def _frame_complete(self):
        print("full frame detected!")
        print(bin_list_to_int(self.output))


    def _handle_warmup(self, state):
        if state is self.sentinel_value:
            self.state = HistoryInterpreter.DETECTED

    def _handle_detected(self, state):
        if state is not self.sentinel_value:
            self.state = HistoryInterpreter.PROCESSING
            self.buffer = [state]

    def _handle_processing(self, state):
            
        self.buffer.append(state)
        if len(self.buffer) == self.max_buffer_size:
            num_low = self.buffer.count(self.low_value)
            num_high = self.buffer.count(self.high_value)
            num_sentinel = self.buffer.count(self.sentinel_value)

            arg = argmax([num_sentinel, num_low, num_high])

            if arg == 0: # This was a sentinel
                self.state = HistoryInterpreter.DETECTED
                self.frame_complete_callback()
            else:
                self.output.append(int(num_high > num_low))

            self.buffer = []


