# LiFi

The moonshot of moonshots. Let's see if we can get this to work...
If this works we'll actually have a pretty frickin cool project.

## Overview
This repo consists of two main components - transmission (tx) and reception
(rx). The transmission code is written in a modular fashion to allow tx through
different mediums. The primary mediums being developed are a computer screen
(such as a dev laptop) and a Unicorn LED PiHat (prod). Transmission from on the
computer screen uses PyQt5 to display a blinking color signal as a rectangle to
the user.

The rx part in this repo is currently being developed as a rough prototype in
python using OpenCV. The eventual goal is to convert this code to something
that can run in real time in the iPhone application. 

## Setup
(Preferably in a venv, using Python3.6.5) 
`pip install -r requirements`

There may be some other requirements for getting QT5 working on your machine...

## Running

### PyQt5 Laptop Tx
`python scripts/run_pyqt_tx.py`

### Unicorn PiHat Tx
`python scripts/run_tx.py`

### Receiving (Prototype)
For the time being, this prototype is being developed on recorded videos.
1. Capture a video on the iPhone in Slow-Mo (240 fps)
2. Edit video so entire video is in Slow-Mo or none of video is in Slow-Mo
    - Find video on phone
    - Click "Edit" button
    - At the very bottom there should be a slider thingy with ticks denoting
    where the video is being played in Slow-Mo vs normal speed
    - Make it all one or the other. 
3. Upload video to your computer
4. `python Lifi/rx.py -v <path to video>`

