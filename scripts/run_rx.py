# import the necessary packages
import argparse
import time
import cv2

import sys
import os
path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not path in sys.path:
    sys.path.insert(1, path)
del path

from Lifi.TargetTracker import TargetTracker
from Lifi.CvHelpers import *

def main():
    """Handles inpur from file or stream, tests the tracker class"""
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("-v", "--video",
                           help="path to the (optional) video file")
    args = vars(arg_parse.parse_args())

    # if a video path was not supplied, grab the reference
    # to the webcam
    if not args.get("video", False):
        vid_stream = VideoStream(src=0).start()
        fps = 30 
    # otherwise, grab a reference to the video file
    else:
        vid_stream = cv2.VideoCapture(args["video"])
        fps = vid_stream.get(cv2.CAP_PROP_FPS)

    # allow the camera or video file to warm up
    time.sleep(2.0)
    stream = args.get("video", False)
    frame = get_frame(vid_stream, stream)
    height, width = frame.shape[0], frame.shape[1]
    # Frame writer
    out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 
            fps, (width,height))
    print(fps)

    # Target tracker is responsible for detecting a target within a frame
    target_tracker = TargetTracker(height, width)

    # keep looping until no more frames
    more_frames = True
    while more_frames:
        markup_frame = target_tracker.track(frame)
        show("frame", markup_frame)
        out.write(markup_frame)
        frame = get_frame(vid_stream, stream)
        if frame is None:
            more_frames = False

    # if we are not using a video file, stop the camera video stream
    if not args.get("video", False):
        vid_stream.stop()

    # otherwise, release the camera
    else:
        vid_stream.release()

    # close all windows
    cv2.destroyAllWindows()
    print(target_tracker.history)


if __name__ == '__main__':
    main()
