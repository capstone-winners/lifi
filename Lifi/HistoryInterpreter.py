
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

    def __init__(self, callback = None, name = "default"):
        self.id = name

        self.sentinel_value = "blue"
        self.low_value = "green"
        self.high_value = "red"
        self.missing_value = "missing"

        self.state = HistoryInterpreter.WARMUP
        self.buffer = []
        self.max_buffer_size = 4

        self.output = []

        if callback is not None:
            self.frame_complete_callback = callback
        else:
            self.frame_complete_callback = self._frame_complete

    def __eq__(self, other): 
        if not isinstance(other, HistoryInterpreter):
            # don't attempt to compare against unrelated types
            print("[HistoryInterpreter] wrong instance type")
            return False 

        return (self.output == other.output 
                and self.buffer == other.buffer 
                and self.state == other.state)
    
    def __str__(self):
        s = "Output: {}\n".format(self.output)
        s += "Buffer: {}\n".format(self.buffer)
        s += "State: {}\n".format(self.state)
        return s

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

    def _frame_complete(self, obj = None):
        print("[History interpretor {}]: full frame detected!".format(self.name))
        print(bin_list_to_int(self.output))


    def _handle_warmup(self, entry):
        if entry is self.sentinel_value:
            self.state = HistoryInterpreter.DETECTED

    def _handle_detected(self, entry):
        if (entry is not self.sentinel_value 
                and entry is not self.missing_value):
            self.state = HistoryInterpreter.PROCESSING
            self.buffer = [entry]

    def _handle_processing(self, entry):
            
        if(entry == self.missing_value):
            print("[History interpretor {}]:".format(self.id)
                + "missing entry")
        self.buffer.append(entry)
        if len(self.buffer) == self.max_buffer_size:
            num_low = self.buffer.count(self.low_value)
            num_high = self.buffer.count(self.high_value)
            num_sentinel = self.buffer.count(self.sentinel_value)
            num_missing = self.buffer.count(self.missing_value)
            
            if num_missing > sum([num_low, num_high, num_sentinel]):
                # we missed a lot of frames. Lets start over.
                print("[History interpretor {}]:".format(self.id)
                        + "missing a lot of frames. resetting...")
                print("\t{}/{} missing".format(num_missing, self.max_buffer_size))
                print("\t{}".format(self.buffer))
                self.state = HistoryInterpreter.WARMUP
                self.ouput = []
                self.buffer = []
                return

            arg = argmax([num_sentinel, num_low, num_high])
            if arg == 0: # This was a sentinel
                self.state = HistoryInterpreter.DETECTED
                self.frame_complete_callback(self)
            else:
                self.output.append(int(num_high > num_low))

            self.buffer = []

def history_to_pretty_str(history):
    s = ""
    count = 0
    for index, entry in enumerate(history):
        if index == 0:
            continue
        
        if entry != history[index - 1]:
            prev = history[index - 1]
            s += "\n{}\t{}".format(prev, count)

            if entry == "blue":
                s+= "\n"
            count = 0
        else:
            count += 1
    return s
