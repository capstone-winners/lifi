#!/usr/bin/env python

#import unicornhat as unicorn
import UnicornWrapper as unicorn 

import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

from Lifi.tx import LifiTx

if __name__ == "__main__":
    unicorn.set_layout(unicorn.AUTO)
    unicorn.rotation(0)
    unicorn.brightness(0.5)

    mymsg = 64
    tx = LifiTx(unicorn)
    tx.run(mymsg)
