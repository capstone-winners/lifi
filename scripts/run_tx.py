#!/usr/bin/env python

#import unicornhat as unicorn
import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

import Lifi.UnicornWrapper as unicorn 
import weakref

from Lifi.tx import LifiTx

if __name__ == "__main__":
    unicorn.set_layout(unicorn.AUTO)
    unicorn.rotation(0)
    unicorn.brightness(0.85)

    mymsg = 69
    tx = LifiTx(weakref.ref(unicorn))
    tx.run(mymsg)
