import cv2 as cv
import numpy as np


def filter(img_):
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
    needle_count = len(needle_contours)
    # only draws and the contours for the number of contour areas detected
    if needle_count == 1:
        cv.drawContours(frame1, needle_contours, 1, 255, cv.FILLED)
    elif needle_count == 2:
        cv.drawContours(frame1, needle_contours, 1, 255, cv.FILLED)
        cv.drawContours(frame2, needle_contours, 0, 255, cv.FILLED)
    else:
        print("ERROR: number of contours is: " + needle_count)
    
    if needle_count == 1:
        return frame1
    elif needle_count == 2:
        return frame1, frame2
    

def contour_maker(pic): 
    blur = cv.medianBlur(pic,5)
    gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
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
    frame1, frame2 = filter(closing)

    return frame1, frame2


pic = cv.imread('static/images/needle1.jpg')
contour_maker(pic)
  
    # cv2.imshow('gray', gray)
    # cv2.imshow('canny',canny)
    # cv2.imshow('closing',closing)
    # cv2.imshow('filtered',filtered)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
