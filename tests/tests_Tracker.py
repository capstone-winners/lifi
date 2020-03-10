import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

import unittest
from Lifi.TargetTracker import TargetTracker, TargetHistory

class TestTargetTracker(unittest.TestCase):

    def setUp():
        tracker = TargetTracker(300, 300)

    def test_custom_nums(self):
        pass

class TestTargetTracker(unittest.TestCase):

    def setUp(self):
        self.history = TargetHistory()

    def test_add_to_history_single_target(self):
        self.history.add_to_history('blue', (0, 0, 10, 10))
        self.history.add_to_history('green', (0, 1, 10, 11))
        self.history.add_to_history('red', (0, 2, 10, 12))
        
        expected = {"last_pos": (0, 2, 10, 12),
                "last_frame": 2,
                "history": ["blue", "green", "red"]}

        actual = self.history.history[0]

        self.assertEqual(actual["last_pos"], expected["last_pos"])
        self.assertEqual(actual["last_frame"], expected["last_frame"])
        self.assertEqual(actual["history"], expected["history"])
    
    def test_add_to_history_two_target(self):
        self.history.add_to_history('blue', (0, 0, 10, 10))
        self.history.add_to_history('green', (0, 0, 10, 11))
        self.history.add_to_history('red', (30, 30, 10, 12))
        
        expected1 = {"last_pos": (0, 0, 10, 11),
                "last_frame": 1,
                "history": ["blue", "green"]}
        
        expected2 = {"last_pos": (30, 30, 10, 12),
                "last_frame": 2,
                "history": ["red"]}
        expected = [expected1, expected2]
        
        self.assertEqual(self.history.history, expected)


    def test_update_history(self):
        start = {"last_pos": (0, 0, 10, 12),
                "last_frame": 0,
                "history": ["blue"]}
        
        expected = {"last_pos": (1, 1, 10, 12),
                "last_frame": 0,
                "history": ["blue", "green"]}

        new = self.history._update_history_entry(start, "green", (1, 1, 10, 12))

        self.assertEqual(new, expected)



if __name__ == '__main__':
    unittest.main()
