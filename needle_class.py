"""
Find the needle point of the image

"""

import cv2 as cv
import numpy as np

from contour import contour_maker

class NeedleBoy():
    
    def __init__(self, frame):
        # Data members -------------------------------------------------------
        self.img = frame
        self.width = frame.shape[1]
        self.right_tip_point = [] #x,y coordinates of the farthest left point of the point of the RIGHT needle
        self.leftmost1 = (0,0) #leftmost point of the right needle contour
        self.bottommost1 = (0,0) #bottom of the right needle contour
        self.topmost1 = (0,0) #top point of the right needle contour
        self.left_tip_point = []
        self.rightmost2 = (0,0)
        self.topmost2 = (0,0)
        self.bottommost2 = (0,0)
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
        frame = np.zeros_like(img_)
        needle_contours = []
        
        # iterate over all the contours and filter out the area
        for i, c in enumerate(contours):
            c_area = cv.contourArea(c)
            # print(i) 
            # print(c_area)
            if self.min_area <= c_area <= self.max_area:
                needle_contours.append(c)
        frame1 = np.zeros_like(img_)
        frame2 = np.zeros_like(img_)
        cv.drawContours(frame1, needle_contours, 1, 255, cv.FILLED)
        cv.drawContours(frame2, needle_contours, 0, 255, cv.FILLED)

            # mask_one = cv.bitwise_and(img_.copy(), frame1)
            # mask1 = cv.bitwise_or(new_frame, mask_one)

            # mask_two = cv.bitwise_and(img.copy(), frame2)
            # mask2 = cv.bitwise_or()
        # cv.imshow('right needle', frame1)
        # cv.imshow('left needle', frame2)
        # cv.waitKey(0)
        # cv.destroyAllWindows()





        # if self.min_area <= c_area <= self.max_area:
        #         mask = np.zeros_like(img_)
        #         cv.drawContours(mask, contours, i, 255, cv.FILLED)
        #         mask = cv.bitwise_and(img_.copy(), mask)
        #         new_frame = cv.bitwise_or(new_frame, mask)
        return frame1, frame2

    def needle_extremes_right(self, _img):
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
            self.leftmost1 = tuple(cnt[cnt[:,:,0].argmin()][0])
            self.bottommost1 = tuple(cnt[cnt[:,:,1].argmax()][0])
            self.topmost1 = tuple(cnt[cnt[:,:,1].argmin()][0])

            cv.circle(self.img, self.leftmost1, 3, (0,0,255),1)
            cv.circle(_img, self.leftmost1, 3, (0,0,255),1)

            # cv.imshow('right contour', _img)
            # cv.waitKey(0)
            # cv.imshow('right contour', self.img)
            # cv.waitKey(0)
            # cv.destroyAllWindows()


    def needle_extremes_left(self, _img):
        """finds the right, bottom, and top most points for the leftmost contour of the image.

        Args:
            _img ([numpy.ndarray]): [blurred b/w image of just the left contour]
        """
        
        contours, _ = cv.findContours(_img.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

        if len(contours) > 0:
            cnt = contours[-1]
            self.rightmost2 = tuple(cnt[cnt[:,:,0].argmax()][0])
            self.bottommost2 = tuple(cnt[cnt[:,:,1].argmax()][0])
            self.topmost2 = tuple(cnt[cnt[:,:,1].argmin()][0])

            cv.circle(self.img, self.rightmost2, 3, (0,0,255),1)
            cv.circle(_img, self.rightmost2, 3, (0,0,255),1)
            
            cv.imshow('left contour', _img)
            cv.waitKey(0)
            cv.imshow('left contour', self.img)
            cv.waitKey(0)
            cv.destroyAllWindows()

    def extend_mask_left(self, mask):
        """extends the mask of the left contour to the left edge of the image.
        This is a modification from the original extend_mask_right. So if that one is jank, this one
        is gonna be kinda messy. But itll work....hopefully
         
        Args:
            mask ([numpy.ndarray]): [blurred b/w image of just the left contour]

        Returns:
            ([numpy.ndarray]): [b/w mask for the whole needle]
        """

        self.needle_extremes_left(mask)
        x_1, y_1 = self.rightmost2
        y_diff = self.rightmost2[1] - self.bottommost2[1]
        x_2 = self.topmost2[0]
        y_2 = self.topmost1[1] - 2 * y_diff #this is janky
        slope = -(y_2 - y_1) / (x_2 - x_1)

        right_mid_point = self.rightmost2
        right_top_point = (self.rightmost2[0] + 5, self.rightmost2[1] + y_diff)
        right_bottom_point = (self.rightmost2[0] + 5, self.bottommost2[1])
        # b = y-mx
        b_1 = right_top_point[1] - (slope * right_top_point[0])
        b_2 = right_bottom_point[1] - (slope * right_bottom_point[0])
        # y = mx+b
        # slope bigger b/c of angle, janky as well
        left_top_point = (self.width, int(1.5 * slope * self.width + b_1))
        left_bottom_point = (self.width, int(slope * self.width + b_2))
        # cut out the needle
        region_of_interest_verticies = (right_bottom_point, right_mid_point, right_top_point,
                                        left_top_point, left_bottom_point)
        self.needle_vertices2 = region_of_interest_verticies
        newmask = self.region_of_interest(np.array([region_of_interest_verticies], np.int32))
        

        return newmask




    def extend_mask_right(self, mask):
        """extends the mask from the needle contour already found to the edge of the image.
        This is set up for the needle coming in from the right side of the screen.
        It do be janky. Can be set up later to detect the direction the needle is in, then extend that
        to the edge.

        Args:
            mask (numpy.ndarray): [b/w image with only needle contour]

        Returns:
            (numpy.ndarray): [b/w mask for the whole needle]
        """
        
        self.needle_extremes_right(mask)
        x_1, y_1 = self.leftmost1
        y_diff = self.leftmost1[1] - self.bottommost1[1]
        x_2 = self.topmost1[0]
        y_2 = self.topmost1[1] - 2 * y_diff # !JANK ALERT!
        slope = -(y_2 - y_1) / (x_2 - x_1)

        left_mid_point = self.leftmost1
        left_top_point = (self.leftmost1[0] + 5, self.leftmost1[1] + y_diff)
        left_bottom_point = (self.leftmost1[0] + 5, self.bottommost1[1])
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
        self.needle_vertices1 = region_of_interest_vertices
        new_mask = self.region_of_interest(np.array([region_of_interest_vertices], np.int32))

        
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

        # self.median_blur = cv.medianBlur(img_, 5)
        # self.gray = cv.cvtColor(self.median_blur, cv.COLOR_BGR2GRAY)
        # self.canny = cv.Canny(self.gray, 40, 300, apertureSize=3)

        # cv.imshow('canny', self.canny)
        # cv.waitKey()

        # dilation_size = 6
        # dilation_type = cv.MORPH_RECT
        # #kernel is 12x30 rectangle, longer in the y direction
        # kernel = cv.getStructuringElement(
        #     dilation_type, (2 * dilation_size, 5 * dilation_size), 
        #     (dilation_size, dilation_size))
        # self.closing = cv.morphologyEx(self.canny, cv.MORPH_CLOSE, kernel, iterations=2)
        # cv.imshow('closing', self.closing)
        # cv.waitKey(0)
        # cv.destroyAllWindows()
        # #blur closing to let img find the contours
        # cnt_blur = cv.medianBlur(self.closing, 9)
        mask1, mask2 = contour_maker(img_)
        #extend_mask calls needle_extremes which assigns the leftmost point(center)
        newmask1 = self.extend_mask_right(mask1)
        newmask2 = self.extend_mask_left(mask2)
        return newmask1, newmask2
        
        


    def process(self):
        """process the full color image
           self.mask is the masked image
           self.needle_extremes finds needlepoint
 
        """
        self.mask1 , self.mask2 = self.needle_mask(self.img)
        self.right_tip_point = self.leftmost1