import unittest
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

from Lifi.CvHelpers import *

class TestCvHelper(unittest.TestCase):

    
    def test_single_frame_colors(self):
        iou = calculate_iou([39, 63, 203, 112], [54, 66, 198, 114])
        
        self.assertAlmostEqual(iou, 0.7980, 4)
    
    def test_single_frame_colors_tuple(self):
        iou = calculate_iou((39, 63, 203, 112), (54, 66, 198, 114))
        
        self.assertAlmostEqual(iou, 0.7980, 4)

    def test_custom_nums(self):
        iou = calculate_iou(
                convert_box_rep((120, 108, 151, 75)), 
                convert_box_rep((126, 104, 148, 77)))
        
        self.assertAlmostEqual(iou, 0.8734, 4)
if __name__ == '__main__':
    unittest.main()
