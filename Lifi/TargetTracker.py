import cv2

from Lifi.HistoryInterpreter import HistoryInterpreter
from Lifi.ShapeDetector import ShapeDetector
from Lifi.CvHelpers import *
from Lifi.GlobalSettings import *

class TargetTracker:

    def __init__(self, height, width):

        self.height = height
        self.width = width
    
        # Color Ranges 
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

        # Create color trackers
        self.greentracker = ColorDetector("green", height, width, 
                [(green_lower, green_upper)])
        self.redtracker = ColorDetector("red", height, width, 
                [(red_lower, red_upper), (red_lower2, red_upper2)])
        self.bluetracker = ColorDetector("blue", height, width, 
                [(blue_lower, blue_upper)])

        self.trackers = [self.greentracker, self.redtracker, self.bluetracker]

        self.history = TargetHistory(self.complete_frame_callback)
        self.history.iou_failed_callback = self.failed_iou_callback
        
        # The number of frames we expect each message to take
        self.fpm = FRAME_SIZE * BUFFER_SIZE 
        self.frame_count = 0
        self.last_detected = 0
        self.detected_frame = False
        self.bin_message = []

        self.failed_iou_debug = {
                "draw": False,
                "frame_num": 0,
                "last_box": None,
                "new_box": None
                }

    def track(self, frame):
        markup_frame = frame.copy()
        for tracker in self.trackers:
            detected, box = tracker.track(frame, markup_frame)
            tracker.show_mask()
            if detected:
                #print("{}\t{}".format(tracker.name, box))
                self.history.add_to_history(detected, box)

        self.history.advance_frame_count()

        self.frame_count += 1
        if (self.frame_count - self.last_detected) % (self.fpm * 3) == 0:
            print("resetting frame_count\n\t{}\n\t{}".format(
                self.frame_count, 
                self.last_detected))

            self.detected_frame = False

        self._add_message_to_frame(markup_frame)
        self._add_failed_iou_to_frame(markup_frame)
        self._add_target_history_detail_to_frame(markup_frame)

        return markup_frame

    def _add_target_history_detail_to_frame(self, frame):
        #   {last_pos: (x, y, w, h),
        #    last_frame: 1,
        #    history_interpreter: <HI obj>,
        #    history: [r g b]}

        estimated_font_size = 22
        font_scale = .3

        for entry in self.history.history:
            hi = entry["history_interpreter"]
            if (len(hi.buffer) == 0 
                    and len(hi.output) == 0):
                continue

            msgs = ["pos: {}".format(entry["last_pos"]),
                "state: {}".format(hi.state),
                "buffer: {}".format(hi.buffer),
                "output: {}".format(hi.output)]

            for index, msg in enumerate(msgs):
                tr_x = entry["last_pos"][0] + entry["last_pos"][2]
                tr_y = entry["last_pos"][1] + int(index 
                        * 2
                        * estimated_font_size * font_scale)

                cv2.putText(frame, msg, (tr_x, tr_y), cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale, (255, 255, 255), 1)


    def _add_message_to_frame(self, frame):
        print(self.frame_count)
        if self.detected_frame:
            msg = "{}: {}".format(self.last_detected, str(self.bin_message))
        else:
            msg = "No msg detected"
        
        cv2.putText(frame, msg, (0, int(self.height * .9)), 
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 2)

    def _add_failed_iou_to_frame(self, frame):
        def draw_box(msg, box, color):
            start_point = (box[0], box[1])
            end_point = (box[0] + box[2], box[1] + box[3])
            thickness = 2
            cv2.rectangle(frame, start_point, end_point, color, thickness) 
            cv2.putText(frame, msg, end_point, 
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 2)

        if(self.failed_iou_debug["draw"]):
            draw_box("last_box", self.failed_iou_debug["last_box"], (255, 0, 0))
            draw_box("new_box", self.failed_iou_debug["new_box"], (0, 255, 0))
            self.failed_iou_debug["draw"] = False

    def failed_iou_callback(self, last_box, this_box):
        self.failed_iou_debug = {
                "draw": True,
                "frame_num": self.frame_count,
                "last_box": last_box,
                "new_box": this_box 
                }
        

    def complete_frame_callback(self, interp):
        print("[Target Tracker]: callback")
        self.detected_frame = True
        self.last_detected = self.frame_count
        self.bin_message = interp.pop_output()

class ColorDetector:
    """
    A basic color detector, it will look for colors in a range and
    create an x and y offset valuefrom the midpoint

    color bounds is a list of ranges [(lower, upper), ...]
    """

    def __init__(self, name, height, width, color_bounds):
        self.name = name

        self.color_bounds = color_bounds
        self.midx = int(width / 2)
        self.midy = int(height / 2)
       
        self.sd = ShapeDetector()

    def track(self, frame, markup=None):
        """Simple HSV color space tracking"""
        # resize the frame, blur it, and convert it to the HSV
        # color space
        blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        # Create a mask based on the colors of this tracker
        self.mask = self._generate_mask(hsv)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(self.mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0]

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the shape and bounding box if its a target
            cnts.sort(key=cv2.contourArea, reverse=True)
            c = first(cnts, lambda x: self.sd.detect(x)[0] == "target")

            shape, box = self.sd.detect(c)

            if markup is not None:
                self._update_markup_frame(markup, c, shape, box)
            
            # only proceed if the shape is a target
            if shape is "target":
                return self.name, box

        return False, None
    
    def _update_markup_frame(self, markup_frame, c, shape, box):
        x, y, _, _ = box
        cv2.drawContours(markup_frame, [c], -1, (0, 255, 255), 2)
        cv2.putText(markup_frame, shape, (int(x), int(y)), 
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (255, 255, 255), 2)

    def _generate_mask(self, hsv):
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
        
        return mask

    def show_mask(self):
        show(self.name + " mask", self.mask)

class TargetHistory():

    def __init__(self, callback = None):
        # [
        #   {last_pos: (x, y, w, h),
        #    last_frame: 1,
        #    history_interpreter: <HI obj>,
        #    history: [r g b]},
        #
        #   {last_pos: (x, y, w, h),
        #    last_frame: 1,
        #    history_interpreter: <HI obj>,
        #    history: [r g b]},
        #
        #   ...
        # ]
        self.history = []
        
        # Max distance between two points in order to match.
        self.max_corresponding_distance = 25    
        # Min iou value for two boxes to match.
        self.iou_threshold = .7

        self.frame = 0
        self.max_frames_to_live = 30

        
        # Callbacks
        if callback is not None:
            self.frame_complete_callback = callback
        else:
            self.frame_complete_callback = self._default_frame_complete

        self.iou_failed_callback = None

    def configure_callback(self, callback):
        self.frame_complete_callback = callback

    def add_to_history(self, detected, box):
        # If the history is empty, just add this one in. 
        if len(self.history) == 0:
            self.history.append(self._create_history_entry(detected,box))
            return

        # Determine what entry has the minimum distance to the new box.
        min_entry = min(self.history, 
                key=lambda x: calculate_distance_center(box, x["last_pos"]))
        min_distance = calculate_distance_center(box, min_entry["last_pos"])
        
        # Consider this a new element:
        if min_distance > self.max_corresponding_distance:
            self.history.append(self._create_history_entry(detected,box))
        else:
            # Get the index of the box with the minimum index
            min_box_index = [calculate_distance_center(box, entry["last_pos"]) 
                    for entry in self.history].index(min_distance)
            min_box = self.history[min_box_index]["last_pos"]

            # Determine if there is enough overlap to be the same
            iou = calculate_iou(convert_box_rep(box), convert_box_rep(min_box))
            if iou > self.iou_threshold:
                self.history[min_box_index] = self._update_history_entry(
                        self.history[min_box_index], detected, box)
            else: 
                print("failed iou threshold!!! {}".format(iou))
                self.iou_failed_callback(min_box, box)
    
    def advance_frame_count(self):

        self._record_no_detections()

        # Increment the frame count and wrap at the max_frames_to_live.
        self.frame = (self.frame + 1) % self.max_frames_to_live
        
        #
        def is_not_missing(entry):
            return entry["history"][-self.max_frames_to_live:].count("missing") != self.max_frames_to_live,

        # Remove any entries which we haven't seen since the frame wrap around.
        self.history = list(filter(is_not_missing, self.history))

    def _record_no_detections(self):
        for entry in self.history:
            if entry["last_frame"] != self.frame:
                entry["last_frame"] = self.frame
                entry["history_interpreter"].process("missing")
                entry["history"].append("missing")

    def _create_history_entry(self, detected, box): 
        interp = HistoryInterpreter(self.frame_complete_callback, str(box))
        interp.max_buffer_size = BUFFER_SIZE
        interp.process(detected)
        return {"last_pos": box,
                "last_frame": self.frame,
                "history_interpreter": interp,
                "history":[detected]}

    def _update_history_entry(self, entry, detected, box):
        entry["history_interpreter"].process(detected)

        return {"last_pos": box,
                "last_frame": self.frame,
                "history_interpreter": entry["history_interpreter"],
                "history": entry["history"] + [detected]}
    
    def _default_frame_complete(self, msg = None):
        print("[TargetHistory] Frame Complete")
    
    def __str__(self):
        s = ""
        for index, entry in enumerate(self.history):
            s += "{}\n".format(index)
            s += "\t{}: {}\n".format("last pos", entry["last_pos"])
            s += "\t{}: {}\n".format("last frame", entry["last_frame"])
            s += "\t{}: {}\n".format("history", entry["history"])
        return s


