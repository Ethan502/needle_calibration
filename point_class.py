"""
Calibration Class for interpreting the nanoPOTS chip images
    Opens image passed in and finds the coordinates of the calibration point center
To implement this class you need to:
    - pass in an image and a needle mask
    - set_roi_vertices(vertices)
    - call self.find_point(img)
    call these before self.find_point() if you want to change settings
        default thresh = (60, 200)
        self.thresh_l = num # initialize lower threshold
        self.thresh_u =  #initialize upper threshold
"""

import cv2 as cv
import numpy as np

class PointFinder:
    # Constructor ---------------------------------------------------------
    def __init__(self, frame):
        # Data members ----------------------------------------------------
        self.img = frame
        self.center = [] # x,y coordinates of the calibration point center
        #outline of the needle, also useful for finding the needle location if it moves
        self.needle_vertices = []
        # [(x,y), (x,y), etc] where x=0 is left and y=0 is top
        self.roi_vertices = []
        self.needle_vertices = []
        self.c_area =[] # gives area of the contour found
        # default/settings
        # threshold filter settings
        self.thresh_l = 60
        self.thresh_u = 250
        self.flag_roi_in_out = 0
        # area filter settings
        self.min_area = 1300
        self.max_area = 2500
        # images during different stages of image processing
        self.gray_img = []
        self.blurred_img = []
        self.cropped_img = []
        self.thresh_img = []
        self.filtered_mask_img = []

    #Filters ---------------------------------------------------------------

    # ROI, Masks inside or outside of the shape given. Mask Outside shape is flag_roi_in_out = 0
    # Mask shape if flag_roi_in_out = 1
    # working with black and white images, so don't need to specify channel count
    def region_of_interest(self, img, vertices):
        #this process keeps pixels inside shape given
        if (self.flag_roi_in_out == 0):
            mask = np.zeros_like(img)
            match_mask_color = (255)
            cv.fillPoly(mask, vertices, (255,255,255))
            cv.bitwise_not(mask)
            masked_image = cv.bitwise_and(img.copy(), mask)
        else:
            # this process masks pixels inside shape given
            mask = cv.bitwise_not(np.zeros_like(img))
            match_mask_color = (0)
            cv.fillPoly(mask, vertices, match_mask_color)
            masked_image = cv.bitwise_and(img, mask)
        return masked_image


    # filters out contours based on min/max areas
    def area_bandpass_filter(self):
        thresh_img = self.thresh_img
        contours, _ = cv.findContours(thresh_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        new_frame = np.zeros_like(thresh_img)
        # loop over the contours, get rid of contours outside the threshold
        for i, contour in enumerate(contours):
            c_area = cv.contourArea(contour)
            if self.min_area <= c_area <= self.max_area:
                self.c_area = c_area
                mask = np.zeros_like(thresh_img)
                cv.drawContours(mask, contours, i, (255,255,255), cv.FILLED)
                mask = cv.bitwise_and(thresh_img.copy(), mask)
                new_frame = cv.bitwise_or(new_frame, mask)
        return new_frame


    # masks the needle
    def needle_filter(self, image):
        self.flag_roi_in_out = 1
        cropped_image = self.region_of_interest(image, np.array([self.needle_vertices], np.int32))
        self.flag_roi_in_out = 0
        return cropped_image


    def find_point(self):
        # find contours in the threshold frame
        contours, _ = cv.findContours(self.filtered_mask_img.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        # approximate contours to polygons + get bounding rects and circles
        contours_poly = [None] * len(contours)
        centers = [None] * len(contours)
        radius = [None] * len(contours)
        for i, c in enumerate(contours):
            contours_poly[i] = cv.approxPolyDP(c, 3, True)
            centers[i], radius[i] = cv.minEnclosingCircle(contours_poly[i])
        for i in range(len(contours)):
            # grab x,y coordinates in center of shape
            self.center = (int(centers[i][0]), int(centers[i][1]))



    # Find point ------------------------------------------------------------
    # implements the class

    def process(self):
        # convert img to grayscale and blur
        self.gray_img = cv.cvtColor(self.img.copy(), cv.COLOR_BGR2GRAY)
        self.blurred_img = cv.medianBlur(self.gray_img.copy(), 9)
        cv.imshow('window', self.blurred_img)
        cv.waitKey(0)
        cv.destroyAllWindows()
        # crop out edges of frame that confuse the cv
        print(self.roi_vertices)
        self.cropped_img = self.region_of_interest(self.blurred_img, np.array([self.roi_vertices], np.int32))
        self.cropped_img = self.needle_filter(self.cropped_img)
        # make a mask to be able to find the dark spots on the frame
        _, self.thresh_img = cv.threshold(self.cropped_img, self.thresh_1, self.thresh_u, cv.THRESH_BINARY_INV)
        #filters contours using area(size) thresholds
        self.filtered_mask_img = self.area_bandpass_filter()
        self.find_point()
        return self.center

