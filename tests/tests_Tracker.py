import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

import unittest
from unittest.mock import MagicMock
from Lifi.TargetTracker import TargetTracker, TargetHistory
from Lifi.HistoryInterpreter import HistoryInterpreter

class TestTargetTracker(unittest.TestCase):

    def setUp(self):
        tracker = TargetTracker(300, 300)

    def test_custom_nums(self):
        pass

class TestTargetHistory(unittest.TestCase):

    def setUp(self):
        self.history = TargetHistory()

    def test_add_to_history_single_target(self):
        interp = HistoryInterpreter()
        interp = self.helper_add_to_history('blue', (0, 0, 10, 10), interp)
        interp = self.helper_add_to_history('green', (0, 1, 10, 11), interp)
        interp = self.helper_add_to_history('red', (0, 2, 10, 12), interp)
        
        expected = {"last_pos": (0, 2, 10, 12),
                "last_frame": 2,
                "history_interpreter": interp,
                "history": ["blue", "green", "red"]}
        actual = self.history.history[0]

        self.compare_history(actual, expected)
    
    def test_trigger_frame_complete(self):
        interp = HistoryInterpreter()

        interp = self.helper_add_to_history('blue', (0, 0, 10, 10), interp)
        interp = self.helper_add_to_history('blue', (0, 0, 10, 10), interp)
        interp = self.helper_add_to_history('blue', (0, 0, 10, 10), interp)
        interp = self.helper_add_to_history('blue', (0, 0, 10, 10), interp)
        interp = self.helper_add_to_history('red', (0, 1, 10, 12), interp)
        interp = self.helper_add_to_history('red', (0, 1, 10, 12), interp)
        interp = self.helper_add_to_history('red', (0, 1, 10, 12), interp)
        interp = self.helper_add_to_history('red', (0, 1, 10, 12), interp)
        interp = self.helper_add_to_history('green', (0, 1, 10, 11), interp)
        interp = self.helper_add_to_history('green', (0, 1, 10, 11), interp)
        interp = self.helper_add_to_history('green', (0, 1, 10, 11), interp)
        interp = self.helper_add_to_history('green', (0, 1, 10, 11), interp)
        interp = self.helper_add_to_history('blue', (0, 0, 10, 10), interp)
        interp = self.helper_add_to_history('blue', (0, 0, 10, 10), interp)
        interp = self.helper_add_to_history('blue', (0, 0, 10, 10), interp)
        interp = self.helper_add_to_history('blue', (0, 0, 10, 10), interp)
        
        expected = {"last_pos": (0, 0, 10, 10),
                "last_frame": 15,
                "history_interpreter": interp,
                "history": [
                    "blue", "blue", "blue", "blue", 
                    "red", "red", "red", "red",
                    "green", "green", "green", "green",
                    "blue", "blue", "blue", "blue", 
                    ]}

        actual = self.history.history[0]
        self.compare_history(actual, expected)
    
    def test_add_to_history_two_target(self):
        self.history.add_to_history('blue', (0, 0, 10, 10))
        self.history.add_to_history('green', (0, 0, 10, 11))
        self.history.add_to_history('red', (30, 30, 10, 12))
        
        interp1 = HistoryInterpreter()
        interp1.process("blue")
        interp1.process("green")
        expected1 = {"last_pos": (0, 0, 10, 11),
                "last_frame": 1,
                "history_interpreter": interp1,
                "history": ["blue", "green"]}
        
        interp2 = HistoryInterpreter()
        interp2.process("red")
        expected2 = {"last_pos": (30, 30, 10, 12),
                "last_frame": 2,
                "history_interpreter": interp2,
                "history": ["red"]}
        expected = [expected1, expected2]
        
        self.compare_history(self.history.history[0], expected[0])
        self.compare_history(self.history.history[1], expected[1])


    def test_update_history(self):

        interp = HistoryInterpreter()

        start = {"last_pos": (0, 0, 10, 12),
                "last_frame": 0,
                "history_interpreter": interp,
                "history": ["blue"]}
        
        expected = {"last_pos": (1, 1, 10, 12),
                "last_frame": 0,
                "history_interpreter": interp,
                "history": ["blue", "green"]}

        new = self.history._update_history_entry(start, "green", (1, 1, 10, 12))

        self.compare_history(new, expected)

    def helper_add_to_history(self, detected, box, interp):
        self.history.add_to_history(detected, box)
        interp.process(detected)
        return interp

    def compare_history(self, hist1, hist2):
        self.assertEqual(hist1["last_pos"], hist2["last_pos"])
        self.assertEqual(hist1["last_frame"], hist2["last_frame"])
        self.assertEqual(hist1["history_interpreter"], hist2["history_interpreter"])
        self.assertEqual(hist1["history"], hist2["history"])



if __name__ == '__main__':
    unittest.main()
