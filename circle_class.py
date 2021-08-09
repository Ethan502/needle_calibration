import cv2 as cv
import numpy as np


class CircleBoy:
    def __init__(self, pic):
        self.img = pic
        self.point = (0,0)

    # filter out the contours of the incorrect size
    def area_bandpass_filter(self, img):
        count = 0
        min_area = 1300
        max_area = 2500
        contours, _ = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
        new_frame =  np.zeros_like(img)
        print(len(contours))
        mask = np.zeros_like(img)
        for i, contour in enumerate(contours):
            c_area = cv.contourArea(contour)
            if min_area <= c_area <= max_area:
                count+=1
                cv.drawContours(mask, contours, i, 255, cv.FILLED)
                mask = cv.bitwise_and(img.copy(), mask)
        print(count)
        return mask

    def center_point_finder(self, img):
        """finds the center point of the detected circle

        Args:
            img ([nd.array]): [b/w mask of just the detected center point]
        """

        cv.imshow('mask', img)
        cv.waitKey()
        cv.destroyAllWindows()


        contours, _ = cv.findContours(img.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            cnt = contours[-1]
            left =  tuple(cnt[cnt[:,:,0].argmin()][0])
            top = tuple(cnt[cnt[:,:,1].argmin()][0])
            bottom = tuple(cnt[cnt[:,:,1].argmax()][0])
            right = tuple(cnt[cnt[:,:,0].argmax()][0])

            top_x, top_y = top[0], top[1]
            bottom_x, bottom_y = bottom[0], bottom[1]
            left_x, left_y = left[0], left[1]
            right_x, right_y = right[0], right[1]

            # center_x = (top_x + bottom_x + left_x + right_x)/4
            # center_y = (top_y + bottom_y + left_y + right_y)/4

            center_x = ((right_x - left_x)/2) + left_x
            center_y = ((bottom_y - top_y)/2) + top_y
            center_point = (round(center_x),round(center_y))
            self.point = center_point



    def process(self):
        lighter_img = np.maximum(self.img.copy(), 10) # gets rid of any black pixels
        foreground = lighter_img.copy()
        seed = (10,10) # using the top left corner as the "background" seed color
        cv.floodFill(foreground, None, seedPoint=seed, newVal=(0,0,0), loDiff=(5,5,5,5), upDiff=(5,5,5,5))
        gray = cv.cvtColor(foreground, cv.COLOR_BGR2GRAY)
        thresh = cv.threshold(gray, 1, 255, cv.THRESH_BINARY)[1]
        thresh = cv.morphologyEx(thresh, cv.MORPH_OPEN, cv.getStructuringElement(cv.MORPH_RECT, (5,5)))
        blur_mask = cv.medianBlur(thresh, 9)
        filtered = self.area_bandpass_filter(blur_mask)
        self.center_point_finder(filtered)
        return self.point

