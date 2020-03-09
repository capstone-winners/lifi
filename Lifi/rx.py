# import the necessary packages
import argparse
import time
import cv2
import imutils
from imutils.video import VideoStream

from ShapeDetector import ShapeDetector

def main():
    """Handles inpur from file or stream, tests the tracker class"""
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("-v", "--video",
                           help="path to the (optional) video file")
    args = vars(arg_parse.parse_args())

    # define the lower and upper boundaries of the "green"
    # ball in the HSV color space. NB the hue range in
    # opencv is 180, normally it is 360
    green_lower = (50, 50, 50)
    green_upper = (70, 255, 255)
    red_lower = (0, 50, 20)
    red_upper = (5, 255, 255)
    red_lower2 = (170, 50, 20)
    red_upper2 = (180, 255, 255)
    blue_lower = (110, 50, 50)
    blue_upper = (130, 255, 255)

    # if a video path was not supplied, grab the reference
    # to the webcam
    if not args.get("video", False):
        vid_stream = VideoStream(src=0).start()
    # otherwise, grab a reference to the video file
    else:
        vid_stream = cv2.VideoCapture(args["video"])
        fps = vid_stream.get(cv2.CAP_PROP_FPS)


    # allow the camera or video file to warm up
    time.sleep(2.0)
    stream = args.get("video", False)
    frame = get_frame(vid_stream, stream)
    height, width = frame.shape[0], frame.shape[1]
    greentracker = Tracker("green", height, width, [(green_lower, green_upper)])
    redtracker = Tracker("red", height, width, [(red_lower, red_upper), (red_lower2, red_upper2)])
    bluetracker = Tracker("blue", height, width, [(blue_lower, blue_upper)])

    # Frame writer
    out = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 
            fps, (width,height))
    print(fps)

    # keep looping until no more frames
    more_frames = True
    while more_frames:
        markup_frame = frame.copy()
        x, y = redtracker.track(frame, markup_frame)
        if x != 0 and y != 0:
            #markup_frame = redtracker.draw_arrows(markup_frame)
            print("red")
        x, y = bluetracker.track(frame, markup_frame)
        if x != 0 and y != 0:
            #markup_frame = bluetracker.draw_arrows(markup_frame)
            print("blue")
        x, y = greentracker.track(frame, markup_frame)
        if x != 0 and y != 0:
            #markup_frame = greentracker.draw_arrows(markup_frame)
            print("green")

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


def get_frame(vid_stream, stream):
    """grab the current video frame"""
    frame = vid_stream.read()
    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if stream else frame
    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        return None
    else:
        frame = imutils.resize(frame, width=600)
        return frame


def show(frame_name, frame):
    """show the frame to cv2 window"""
    cv2.imshow(frame_name, frame)
    key = cv2.waitKey(1) & 0xFF

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        exit()

class Tracker:
    """
    A basic color tracker, it will look for colors in a range and
    create an x and y offset valuefrom the midpoint

    color bounds is a list of ranges [(lower, upper), ...]
    """

    def __init__(self, name, height, width, color_bounds):
        self.name = name
        self.color_bounds = color_bounds
        self.midx = int(width / 2)
        self.midy = int(height / 2)
        self.xoffset = 0
        self.yoffset = 0

    def draw_arrows(self, frame):
        """Show the direction vector output in the cv2 window"""
        #cv2.putText(frame,"Color:", (0, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, thickness=2)
        if self.xoffset != 0 and self.yoffset != 0:
            cv2.arrowedLine(frame, (self.midx, self.midy),
                            (self.midx + self.xoffset, self.midy - self.yoffset),
                            (255, 0, 255), 5)
        return frame

    def track(self, frame, markup=None):
        """Simple HSV color space tracking"""
        # resize the frame, blur it, and convert it to the HSV
        # color space
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # construct a mask for the color then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = None
        for color_range in self.color_bounds:
            color_lower = color_range[0]
            color_upper = color_range[1]
            mask_temp  = cv2.inRange(hsv, color_lower, color_upper)
            mask = mask_temp if mask is None else mask | mask_temp

        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0]
        center = None
        self.xoffset = 0
        self.yoffset = 0

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        
            sd = ShapeDetector()

            # only proceed if the radius meets a minimum size
            if radius > 20:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                #cv2.circle(frame, (int(x), int(y)), int(radius),
                #           (0, 255, 255), 2)
                #cv2.circle(frame, center, 5, (0, 0, 255), -1)
                shape = sd.detect(c)
                if markup is not None and shape is "target":
                    self.xoffset = int(center[0] - self.midx)
                    self.yoffset = int(self.midy - center[1])
                    cv2.drawContours(markup, [c], -1, (0, 255, 255), 2)
                    cv2.putText(markup, shape, (int(x), int(y)), 
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (255, 255, 255), 2)

        show(self.name + " mask", mask)

        return self.xoffset, self.yoffset

if __name__ == '__main__':
    main()
