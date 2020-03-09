import unittest
from Lifi.tx import *

class TestLifiMsgEncoder(unittest.TestCase):

    def test_int_to_bin(self):
        expected256 = [0]*16
        expected256[-9] = 1
        expected64 = [0, 1, 0, 0, 0, 0, 0, 0]
        expected32 = [0, 0, 1, 0, 0, 0, 0, 0]

        self.assertEqual(len(LifiMsgEncoder._int_to_bin_list(256)), len(expected256))
        self.assertEqual(LifiMsgEncoder._int_to_bin_list(256), expected256)
        self.assertEqual(LifiMsgEncoder._int_to_bin_list(64), expected64)
        self.assertEqual(LifiMsgEncoder._int_to_bin_list(32), expected32)

    def test_chunker(self):
        seq = range(0,8)
        expected = [range(0, 4), range(4, 8)]
        self.assertEqual(list(LifiMsgEncoder._chunker(seq, 4)), expected)

    def test_msg_to_frame(self):
        test = LifiMsgEncoder.msg_to_frame(64)
        expected64 = LifiMsgEncoder.preamble \
                        + [0, 1, 0, 0, 0, 0, 0, 0] \
                        + [1, 0, 0, 0]
        
        self.assertEqual(test, [expected64])

class TestLifiMsgTx(unittest.TestCase):

    def test_frame_colors(self):
        tx = LifiTx(None)

        exp_seq = [(255, 0, 0), (0, 255, 0), (0, 255, 0)]
        seq = tx._frames_to_colors([[1, 0, 0]])
        
        self.assertEqual(seq, exp_seq)
    
    def test_single_frame_colors(self):
        tx = LifiTx(None)

        exp_seq = [(255, 0, 0), (0, 255, 0), (0, 255, 0)]
        seq = tx._frame_to_colors([1, 0, 0])
        
        self.assertEqual(seq, exp_seq)

if __name__ == '__main__':
    unittest.main()
