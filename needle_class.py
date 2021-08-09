"""
Find the needle point of the image

"""

import cv2 as cv
import numpy as np

from contour_needle import contour_maker

class NeedleBoy():
    
    def __init__(self, frame):
        # Data members -------------------------------------------------------
        self.img = frame
        self.width = frame.shape[1]
        self.right_tip_point = [] #x,y coordinates of the farthest left point of the point of the RIGHT needle
        self.left_tip_point = [] #x,y coordinates of the farthest right point of the LEFT needle
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
        # focused needle count
        self.needle_count = 0

    def filter(self,img_):
        contours, _ = cv.findContours(img_.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        needle_contours = []
        frame1 = np.zeros_like(img_)
        frame2 = np.zeros_like(img_)
        # iterate over all the contours and filter out the area
        for c in contours:
            c_area = cv.contourArea(c)
            # print(i) 
            # print(c_area)
            if 10000 <= c_area <= 400000:
                needle_contours.append(c)
        self.needle_count = len(needle_contours)
        print(f"The number of contours is: {self.needle_count}")
        # only draws and the contours for the number of contour areas detected
        if self.needle_count == 1:
            cv.drawContours(frame1, needle_contours, 1, 255, cv.FILLED)
        elif self.needle_count == 2:
            cv.drawContours(frame1, needle_contours, 1, 255, cv.FILLED)
            cv.drawContours(frame2, needle_contours, 0, 255, cv.FILLED)
        else:
            print("ERROR: number of contours is: " + self.needle_count)
        
        if self.needle_count == 1:
            return frame1, None
        elif self.needle_count == 2:
            return frame1, frame2


    def contour_maker(self,pic): 
        blur = cv.medianBlur(pic,5)
        lab = cv.cvtColor(blur, cv.COLOR_BGR2LAB)
        lab_planes = cv.split(lab)
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        lab_planes[0] = clahe.apply(lab_planes[0])
        lab = cv.merge(lab_planes)
        canny = cv.Canny(lab, threshold1=40, threshold2=300, apertureSize=3)
        dilation_size = 6
        dilation_type = cv.MORPH_RECT
        kernel = cv.getStructuringElement(
                    dilation_type, (2 * dilation_size, 5 * dilation_size), 
                    (dilation_size, dilation_size))
        closing = cv.morphologyEx(canny, cv.MORPH_CLOSE, kernel, iterations=2)
        frame1, frame2 = self.filter(closing)

        return frame1, frame2


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
            
            cv.imshow('result', self.img)
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
        mask1, mask2 = self.contour_maker(img_)
        #extend_mask calls needle_extremes which assigns the leftmost and rightmost points
        
        if self.needle_count == 1:
            newmask1 = self.extend_mask_right(mask1)
            return newmask1
        elif self.needle_count == 2:
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
        self.left_tip_point = self.rightmost2