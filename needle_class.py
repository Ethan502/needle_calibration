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
        stuff = []
        
        # iterate over all the contours and filter out the area
        for i, c in enumerate(contours):
            c_area = cv.contourArea(c)
            print(i)
            print(c_area)
            if self.min_area <= c_area <= self.max_area:
                stuff.append(c_area)
                mask = np.zeros_like(img_)
                cv.drawContours(mask, contours, i, 255, cv.FILLED)

        print(stuff)
        cv.imshow('new', mask)
        cv.waitKey(0)
        cv.destroyAllWindows()

    
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

        dilation_size = 6
        dilation_type = cv.MORPH_RECT
        #kernel is 12x30 rectangle, longer in the y direction
        kernel = cv.getStructuringElement(
            dilation_type, (2 * dilation_size, 5 * dilation_size), 
            (dilation_size, dilation_size))
        self.closing = cv.morphologyEx(self.canny, cv.MORPH_CLOSE, kernel, iterations=2)
        #blur closing to let img find the contours
        cnt_blur = cv.medianBlur(self.closing, 9)
        cv.imshow('contoured', cnt_blur)
        needle_area_filter = self.area_bandpass_filter(cnt_blur)
        #extend_mask calls needle_extremes which assigns the leftmost point(center)

        
        


    def process(self):
        """process the full color image
           self.mask is the masked image
           self.needle_extremes finds needlepoint
 
        """
        self.mask = self.needle_mask(self.img)
        self.point = self.leftmost