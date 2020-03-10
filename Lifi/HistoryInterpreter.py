
# States
# 0 - warm_up
# 1 - detected
# 2 - processing
# 
# [g r r b b b b g g g g r r r r g g g r b b b b g g g g]
#  0 0 0 1 1 1 1 2 2 2 2 2 2 2 2 2 2 2 2 1 1 1 1 2 2 2 2
#    -       -      0       1       0

WARMUP = 0
DETECTED = 1
PROCESSING = 2

class HistoryInterpreter():

    def __init__(self):
        self.sentinel = "blue"
        self.low_value = "green"
        self.high_value = "red"

        self.state = WARMUP
        self.buffer = []
        self.max_buffer_size = 4

        self.output = []

    def process(self, history):
        for entry in history:
            if self.state == WARMUP:
                self._handle_warmup(entry)
            elif self.state == DETECTED:
                self._handle_detected(entry)
            elif self.state == PROCESSING:
                self._handle_processing(entry)

    def _handle_warmup(self, state):
        if state is self.sentinel:
            self.state = DETECTED

    def _handle_detected(self, state):
        if state is not self.sentinel:
            self.state = PROCESSING
            self.buffer = [state]

    def _handle_processing(self, state):
        def process_buffer():
            num_low = self.buffer.count(self.low_value)
            num_high = self.buffer.count(self.high_value)
            self.output.append(int(num_high > num_low))
            self.buffer = []
            
        if state is self.sentinel:
            # If we get a sentinel but have already processed started reading 
            # more than half a bufer, then just process the buffer. 
            if len(self.buffer) >= self.max_buffer_size/2:
                process_buffer()
            self.state = DETECTED
            return 
        
        self.buffer.append(state)
        if len(self.buffer) == self.max_buffer_size:
            process_buffer()


