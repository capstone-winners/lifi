import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

import unittest
from Lifi.HistoryInterpreter import HistoryInterpreter
from tests.dummy_sequence import dummy_history

class TestHistoryInterpreter(unittest.TestCase):

    def setUp(self):
        self.hi = HistoryInterpreter()

    def test_process_clean(self):
        test = ["green", "green", 
                "blue", "blue", "blue", "blue", 
                "red", "red", "red", "red",
                "green", "green", "green", "green",
                "red", "red", "red", "red",
                "blue", "blue", "blue", "blue", 
               ]
        expected = [1, 0, 1]
        
        self.hi.process_batch(test)
        self.assertEqual(self.hi.output, expected)
    
    def test_process_missed_frame(self):
        test = ["green", "green", 
                "blue", "blue", "blue", "blue", 
                "green", "green", "green", # missing frame here
                "red", "red", "red", "red",
                "blue", "blue", "blue", "blue", 
               ]
        expected = [0, 1]
        
        self.hi.process_batch(test)
        self.assertEqual(self.hi.output, expected)
    
    def test_process_flipped_frame(self):
        test = ["green", "green", 
                "blue", "blue", "blue", "blue", 
                "green", "green", "green", "red", # Flipped frame here
                "red", "red", "red", "red",
                "blue", "blue", "blue", "blue", 
               ]
        expected = [0, 1]
        
        self.hi.process_batch(test)
        self.assertEqual(self.hi.output, expected)
    
    def test_process_extra_frame(self):
        test = ["green", "green", 
                "blue", "blue", "blue", "blue", 
                "green", "green", "green", "green", "green", # Extra frame here
                "red", "red", "red", "red",
                "blue", "blue", "blue", "blue", 
               ]
        expected = [0, 1]
        
        self.hi.process_batch(test)
        self.assertEqual(self.hi.output, expected)
    
    def test_process_unexpected_sentinel(self):
        test = ["green", "green", 
                "blue", "blue", "blue", "blue", 
                "green", "green", "green", "green", "blue", # Extra frame here
                "red", "red", "red", "red",
                "blue", "blue", "blue", "blue", 
               ]
        expected = [0, 1]
        
        self.hi.process_batch(test)
        self.assertEqual(self.hi.output, expected)
        
    def test_process_unexpected_sentinel2(self):
        self.hi.output = []
        test = ["green", "green", 
                "blue", "blue", "blue", "blue", 
                "green", "green", "green", "blue", # Extra frame here
                "red", "red", "red", "red",
                "blue", "blue", "blue", "blue", 
               ]
        
        expected = [0, 1]
        self.hi.process_batch(test)
        self.assertEqual(self.hi.output, expected)
    
    def test_pop_output(self):
        self.hi.output = []
        test = ["green", "green", 
                "blue", "blue", "blue", "blue", 
                "green", "green", "green", "blue", # Extra frame here
                "red", "red", "red", "red",
                "blue", "blue", "blue", "blue", 
               ]
        
        expected = [0, 1]
        self.hi.process_batch(test)
        self.assertEqual(self.hi.pop_output(), expected)
        self.assertEqual(self.hi.output, [])
    
    def test_change_to_detected(self):
        self.hi.output = []
        test = ["green", "green", 
                "blue", "blue", "blue", "blue", 
                "green", "green", "green", "blue", # Extra frame here
                "red", "red", "red", "red",
                "blue", "blue", "blue", "red", 
               ]
        
        expected = [0, 1]
        self.hi.process_batch(test)
        self.assertEqual(self.hi.pop_output(), expected)
        self.assertEqual(self.hi.state, HistoryInterpreter.DETECTED)


if __name__ == '__main__':
    unittest.main()
