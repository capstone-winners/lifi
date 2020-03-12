# import the necessary packages
import cv2
class ShapeDetector:
    def __init__(self):
        pass
    def detect(self, c):
        # initialize the shape name and approximate the contour
        shape = "unidentified"
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.03 * peri, True)
        box = cv2.boundingRect(approx)

        # if the shape is a triangle, it will have 3 vertices
        if len(approx) == 3:
            shape = "triangle"
        # if the shape has 4 vertices, it is either a square or
        # a rectangle
        elif len(approx) == 4:
        
            # compute the bounding box of the contour and use the
            # bounding box to compute the aspect ratio
            (x, y, w, h) = box
            ar = w / float(h)
            b_area = w*h
            c_area = cv2.contourArea(c)

            # Make sure the countour area is pretty similar to the estimated
            # bounding box area. This will eliminate any weird, poor shapes
            # that get computed.
            if abs(c_area - b_area) > .7 * b_area:
                # Bad shape approx
                shape = "weird"
                return shape, box
            # 
            # a square will have an aspect ratio that is approximately
            # equal to one, otherwise, the shape is a rectangle
            if ar >= 0.75 and ar <= 1.25:
                shape = "target" 
            else:
                shape = "zzz_rectangle " + str(ar)
            
            if ar >= 1.75 and ar <= 2.25:
                shape = "target"

        # if the shape is a pentagon, it will have 5 vertices
        elif len(approx) == 5:
            shape = "pentagon"
            # otherwise, we assume the shape is a circle
        else:
            shape = "circle"
        
        # return the name of the shape
        return shape, box
