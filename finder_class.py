# needle_cirlce_class.py

import cv2 as cv

from matplotlib import pyplot as plt
from point_class import PointFinder
from needle_class import NeedleBoy
from circle_class import CircleBoy

class CalibrationPoints:
    """finds the calibration point and the needle point

    Args:
        frame np.ndarray: [full color image of needle and calibration point]
    """
    # Constructor------------------------------------------------------------------
    def __init__(self, frame):
        # Data members
        self.img = frame
        self.needle_point = (0,0)
        self.calib_point = (0,0)
        self.debug_flag = False

    def open_subplot_window(self, titles_, images_, subx, suby):
        """plots the images you pass in. you need to specify what subx and suby will be

        Args:
            titles_ (list): [list of labels for images]
            images_ (list): [list of images to plot]
            subx (int): [number of rows]
            suby (int): [number of columns]
        """
        print('open_subplot_window')
        plt.figure()
        for i in range(len(titles_)):
            plt.subplot(subx, suby, i + 1)
            # plots grayscale of all images but RGB
            plt.imshow(images_[i], cmap='gray', vmin=0, vmax = 255)
            plt.title(titles_[i])
            plt.xticks([]), plt.yticks([])

    def debug(self, nf_, pt_):
        print('needle_point: ' + str(self.needle_point))
        print('calib_point: ' + str(self.calib_point))

        points_img = self.img.copy()
        cv.circle(points_img, self.needle_point, 4, (255,0,0), thickness = 6)
        if self.calib_point != []:
            cv.circle(points_img, self.calib_point, 4, (0,255,0),thickness=6)

        titles = ['n_median_blur', 'n_gray', 'n_canny', 'n_closing', 'n_mask',
                  'c_cropped', 'c_thresh', 'c_filtered_mask', 'points']

        images = [
            cv.cvtColor(nf_.median_blur, cv.COLOR_BGR2RGB),
            nf_.gray,
            nf_.canny,
            nf_.closing,
            nf_.mask,
            pt_.cropped_img,
            pt_.thresh_img,
            pt_.filtered_mask_img,
            cv.cvtColor(points_img, cv.COLOR_BGR2RGB),
        ]
        self.open_subplot_window(titles, images, subx=3, suby=3)

    def process(self):
        # needle class implementaion
        nf = NeedleBoy(self.img)
        nf.process()
        self.rightpoint = nf.right_tip_point
        self.leftpoint = nf.left_tip_point
        needle_vertices = nf.needle_vertices1

        # calibration circle implementation
        pt = CircleBoy(self.img)
        # initialize some variables for PointFinder
        # get dimensions of img
        height = pt.img.shape[0]
        width = pt.img.shape[1]
        # this returns the inside of the vertices this one is a square over the image
        # x=0 is left of img and y=0 is top of image
            # pt.roi_vertices = [(width/16,0), (width/16, height * 15 / 16), 
            #                     (width * 15 / 16, height * 15 / 16),
            #                     (width * 15 / 16, 0)]
            
            # pt.needle_vertices = needle_vertices
        

        # init settings
        # lighting thresholds
        # pt.thresh_l = 65
        # pt.thresh_u = 250
        # contour area thresholds
        # pt.min_area = 1300
        # pt.max_area = 2800
        # execute the point class
        self.calib_point = pt.process()
        cv.circle(self.img, self.rightpoint, 1, (0,0,255),2)
        cv.circle(self.img, self.leftpoint, 1, (0,0,255),2)
        cv.circle(self.img, self.calib_point, 1, (255,0,0),2)

        cv.imshow('result', self.img)
        cv.waitKey()
        cv.destroyAllWindows()

        if self.calib_point == []:
            print('not found')
        if self.debug_flag is True:
            self.debug(nf, pt)
            plt.show()
