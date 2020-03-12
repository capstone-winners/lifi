import cv2
import imutils
from imutils.video import VideoStream

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
    return key

def calculate_distance_center(boxA, boxB):
    cx_A = boxA[0] + (boxA[2]/2)
    cy_A = boxA[1] + (boxA[3]/2)

    cx_B = boxB[0] + (boxB[2]/2)
    cy_B = boxB[1] + (boxB[3]/2)

    return ((cx_A-cx_B)**2 + (cy_A-cy_B)**2)**.5

def convert_box_rep(box):
    # converts from [x, y, w, h] to [x1, y1, x2, y2]
    
    return (box[0], box[1], box[0] + box[2], box[1] + box[3])

def calculate_iou(boxA, boxB):
    # expects format to be [x1, y1, x2, y2]

    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    # return the intersection over union value
    return iou

def bin_list_to_int(bin_list):
    return int("".join(str(x) for x in bin_list), 2)

def argmax(l):
    f = lambda i: l[i]
    return max(range(len(l)), key=f)

def first(iterable, condition = lambda x: True):
    try:
        return next(x for x in iterable if condition(x))
    except StopIteration:
        return iterable[0]
