"""
Find the needle point of the image

"""

import cv2 as cv
import numpy as np

class NeedleBoy():
    
    def __init__(self, frame):
        # Data members -------------------------------------------------------
        self.img = frame
        self.width = frame.shape[1]
        self.point = [] #x,y coordinates of the calibration point center
        self.leftmost = (0,0) #leftmost point of the needle contour
        self.bottommost = (0,0) #bottom of the needle contour
        self.topmost = (0,0) #top point of the needle contour
        # area filters settings-----------------------------------------------
        self.min_area = 10000
        self.max_area = 40000
        # images used during different stages of the class--------------------
        self.median_blur = []
        self.gray = []
        self.canny = []
        self.closing = []
        self.mask = []

    def region_of_interest(self, vertices):
        """creates a mask on a grayscale img_ for vertices given

        Args:
            vertices (list): [points for where to put the mask]

        Returns:
            np.ndarray: [grayscale image with vertices mask placed]
        """

        mask = (np.zeros_like(self.img))
        match_mask_color = (255,255,255)
        masked_img = cv.fillPoly(mask, vertices, match_mask_color)
        return masked_img




    def area_bandpass_filter(self, img_):
        """filters the contours out of img_ if they're too small or too big

        Args:
            img_ (np.ndarray): [b/w img that has been thresholded]
            min_area (int): [minimum acceptable area for the contours]
            max_area (int): [maximum acceptable area for the contours]

        Returns:
            (np.ndarray): [b/w img with large and small contours removed]
        """

        contours, _ = cv.findContours(img_.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        new_frame = np.zeros_like(img_)
        # mask = np.zeros_like(img_)
        # cv.drawContours(mask, contours, 1, 255, cv.FILLED)
        # print(contours[3])
        
        # iterate over all the contours and filter out the area
        for i, c in enumerate(contours):
            c_area = cv.contourArea(c)
            print(i)
            print(c_area)
            if self.min_area <= c_area <= self.max_area:
                mask = np.zeros_like(img_)
                cv.drawContours(mask, contours, i, 255, cv.FILLED)
                mask = cv.bitwise_and(img_.copy(), mask)
                new_frame = cv.bitwise_or(new_frame, mask)
        return new_frame

    def needle_extremes(self, _img):
        """finds the left, bottom, and topmost points of the rightmost contour in grayscale
        img that only has the needles in it.

        Args:
            _img (numpy.ndarray): [blurred b/w img that has the contoured needle]
        """

        contours, _ = cv.findContours(_img.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

        if len(contours) > 0:
            cnt = contours[-1]
            print(cnt)
            print(cnt.shape)
            print(type(cnt))
            self.leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
            self.bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])
            self.topmost = tuple(cnt[cnt[:,:,1].argmin()][0])

    def extend_mask(self, mask):
        """extends the mask from the needle contour already found to the edge of the image.
        This is set up for the needle coming in from the right side of the screen.
        It do be janky. Can be set up later to detect the direction the needle is in, then extend that
        to the edge.

        Args:
            mask (numpy.ndarray): [b/w image with only needle contour]

        Returns:
            (numpy.ndarray): [b/w mask for the whole needle]
        """

        self.needle_extremes(mask)
        x_1, y_1 = self.leftmost
        y_diff = self.leftmost[1] - self.bottommost[1]
        x_2 = self.topmost[0]
        y_2 = self.topmost[1] - 2 * y_diff # !JANK ALERT!
        slope = -(y_2 - y_1) / (x_2 - x_1)

        left_mid_point = self.leftmost
        left_top_point = (self.leftmost[0] + 5, self.leftmost[1] + y_diff)
        left_bottom_point = (self.leftmost[0] + 5, self.bottommost[1])
        # b = y-mx
        b_1 = left_top_point[1] - (slope * left_top_point[0])
        b_2 = left_bottom_point[1] - (slope * left_bottom_point[0])
        # y = mx+b
        # slope bigger b/c of angle, also is janky
        right_top_point = (self.width, int(1.5 * slope * self.width + b_1))
        right_bottom_point = (self.width, int(slope * self.width + b_2))
        # cut out needle
        region_of_interest_vertices = (left_bottom_point, left_mid_point, left_top_point,
                                       right_top_point, right_bottom_point)
        self.needle_vertices = region_of_interest_vertices
        new_mask = self.region_of_interest(np.array([region_of_interest_vertices], np.int32))

        cv.imshow('window2', new_mask)
        cv.waitKey(0)
        cv.destroyAllWindows()
        return new_mask
       
    def needle_mask(self, img_):
        """Needlemasking process:
            -medianBlur kernel size 5
            -grayscale
            -canny lines to get needle outlines
            -closing (dilation then erode) to fill the inside of the canny lines
                -kernal is a 12x30 rectangle to fill inside of the needle outline
                -medianBlur again to get rid of sharper edges
                find bottommost point for extending the mask
        Args:
            img_ ([numpy.ndarray]): [image you want to grab]

        Returns:
            [numpy.ndarray]: [the needle mask]
        """

        self.median_blur = cv.medianBlur(img_, 5)
        self.gray = cv.cvtColor(self.median_blur, cv.COLOR_BGR2GRAY)
        self.canny = cv.Canny(self.gray, 40, 300, apertureSize=3)
        cv.imshow('canny', self.canny)

        dilation_size = 6
        dilation_type = cv.MORPH_RECT
        #kernel is 12x30 rectangle, longer in the y direction
        kernel = cv.getStructuringElement(
            dilation_type, (2 * dilation_size, 5 * dilation_size), 
            (dilation_size, dilation_size))
        self.closing = cv.morphologyEx(self.canny, cv.MORPH_CLOSE, kernel, iterations=2)
        #blur closing to let img find the contours
        cnt_blur = cv.medianBlur(self.closing, 9)
        needle_area_filter = self.area_bandpass_filter(cnt_blur)
        #extend_mask calls needle_extremes which assigns the leftmost point(center)
        newmask = self.extend_mask(needle_area_filter)
        return newmask
        
        


    def process(self):
        """process the full color image
           self.mask is the masked image
           self.needle_extremes finds needlepoint
 
        """
        self.mask = self.needle_mask(self.img)
        self.point = self.leftmost