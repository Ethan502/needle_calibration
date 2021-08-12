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
        """[recieved the black and white image from the contouring function, then filters out the contours not in the needed area]
        Args:
            img_ ([numpy.ndarray]): [b/w image of a bunch of contours]
        Returns:
            [numpy.ndarray]: [returns one or two masks with a needle contour on each, depending on how many contours are detected]
        """
        contours, _ = cv.findContours(img_.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        needle_contours = []
        frame1 = np.zeros_like(img_)
        frame2 = np.zeros_like(img_)
        # iterate over all the contours and filter out the area
        for c in contours:
            c_area = cv.contourArea(c)
            # print(i) 
            # print(c_area)
            if 10000 <= c_area <= 40000:
                needle_contours.append(c)
        self.needle_count = len(needle_contours) # variable to determine how many needles are found and how many masks are made
        print(f"The number of needle contours is: {self.needle_count}")
        # only draws and the contours for the number of contour areas detected
        if self.needle_count == 1:
            cv.drawContours(frame1, needle_contours, 0, 255, cv.FILLED)
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
        """function will take the picture, and go through a contouring process to find the ends of the needle then create a mask 
        Args:
            pic ([numpy.ndarray]): [the original picture from cv.imread]
        Returns:
            [numpy.ndarray]: [will change the picture into the correct number of masks based off the found number of needle contours]
        """
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

        if self.needle_count == 1:
            return frame1, None
        elif self.needle_count == 2:
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
            self.leftmost1 = tuple(cnt[cnt[:,:,0].argmin()][0])
            self.bottommost1 = tuple(cnt[cnt[:,:,1].argmax()][0])
            self.topmost1 = tuple(cnt[cnt[:,:,1].argmin()][0])


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
           
       
    def needle_mask(self, img_):
        """
        Args:
            img_ ([numpy.ndarray]): [image you want to grab]
        Returns:
            [numpy.ndarray]: [the needle mask]
        """
        mask1, mask2 = self.contour_maker(img_)
        #calls needle_extremes which assigns the leftmost and rightmost points depending on the number of found contours
        if self.needle_count == 1:
            newmask1 = self.needle_extremes_right(mask1)
            return newmask1, None
        elif self.needle_count == 2:
            newmask1 = self.needle_extremes_right(mask1)
            newmask2 = self.needle_extremes_left(mask2)
            return newmask1, newmask2
        
        


    def process(self):
        """process the full color image
           self.mask is the masked image
           self.needle_extremes finds needlepoint
 
        """
        self.mask1 , self.mask2 = self.needle_mask(self.img)
        self.right_tip_point = self.leftmost1
        self.left_tip_point = self.rightmost2