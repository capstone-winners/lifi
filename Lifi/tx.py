#!/usr/bin/env python

import time
import numpy as np


class LifiTx:

    shift_frequency = 10
    tx_frequency = 30
    color_dict = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue":(0, 0, 255)
            }

    def __init__(self, display):
        self.display = display

    def run(self, my_msg):
        """ my_msg is an integer greater than 0"""
        bin_msg = LifiMsgEncoder.msg_to_frame(my_msg)
        color_sequence = self._frames_to_colors(bin_msg)
        
        while(True):
            for color in color_sequence:
                self._display_color(color)
                self._sleep_frequency()
            self._display_color(self.color_dict["blue"])
            self._sleep_phase_shift()


    def _sleep_frequency(self):
        """ Sleeps for enough time to blink at the desired frequency """

        time.sleep(1.0/LifiTx.tx_frequency)
    
    def _sleep_phase_shift(self):
        """ Sleeps for enough time shift the blink frequency """

        time.sleep(1.0/LifiTx.shift_frequency)

    def _get_color_config(self, rgb):
        """ Get a color configuration for the entire 8x8 grid """
        config = []
        for i in range(8):
            blah = []
            for j in range(8):
                blah.append(rgb)
            config.append(blah) 
        return config
        #return [[(rgb)*8]*8]

    def _display_color(self, rgb):
        """ Changes the entire 8x8 grid to the given color """

        self.display.set_pixels(self._get_color_config(rgb))
        self.display.show_colors()

    def _frames_to_colors(self, bin_frames):
        flatten = lambda l: [item for sublist in l for item in sublist]

        return self._frame_to_colors(flatten(bin_frames))

    def _frame_to_colors(self, bin_frame):
        """ Converts the given msg to a color sequence """
        def helper(value):
            return self.color_dict["red"] if value else self.color_dict["green"]

        return [helper(value) for value in bin_frame]

class LifiMsgEncoder:
    
    preamble = [1, 0, 1, 1, 0, 0]

    def msg_to_frame(msg):
        """ msg should be an integer between 0 and 255 """
        bin_msg = LifiMsgEncoder._int_to_bin_list(msg)
        
        if len(bin_msg) % 8 != 0:
            print("WARNING!!! MESSAGE WRONG DIMENSIONS LENGTH")
        
        def helper(msg_chunk):
            return LifiMsgEncoder.preamble \
            + msg_chunk \
            + LifiMsgEncoder._calculate_parity(msg_chunk)

        return [helper(chunk) for chunk in LifiMsgEncoder._chunker(bin_msg, 8)]


    def _chunker(seq, size):
        """ Breaks a sequence up to chunks of a given size. returned as a [[]] """
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    def _int_to_bin_list(num):
        """ Converts a number to a binary list """
        bin_list = [int(x) for x in bin(num)[2:]]
        mod8 = 8 - len(bin_list)%8

        return [0]*mod8 + bin_list

    def _calculate_parity(bin_msg):

        if len(bin_msg) != 8:
            print("WARNING!!! message wrong size for parity")

        parity = []
        for starter in range(4):
            count = 0
            for window in range(2):
                if bin_msg[(2*starter) + window]:
                    count += 1
            parity.append(count % 2)
        return parity



