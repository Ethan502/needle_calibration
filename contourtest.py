import cv2
import numpy as np


def filter(img_):
    contours, _ = cv2.findContours(img_.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    needle_contours = []
    frame1 = np.zeros_like(img_)
    frame2 = np.zeros_like(img_)
    # iterate over all the contours and filter out the area
    for c in contours:
        c_area = cv2.contourArea(c)
        # print(i) 
        # print(c_area)
        if 10000 <= c_area <= 400000:
            needle_contours.append(c)
    print(len(needle_contours))
    cv2.drawContours(frame1, needle_contours, 1, 255, cv2.FILLED)
    cv2.drawContours(frame2, needle_contours, 0, 255, cv2.FILLED)
    cv2.imshow('frame1',frame1)
    cv2.imshow('frame2', frame2)
    cv2.waitKey()
    cv2.destroyAllWindows()
    return frame1, frame2

    

def contour_maker(pic): 
    pic = np.maximum(pic, 10)
    foreground = pic.copy()
    seed = (10,10)
    cv2.floodFill(foreground, None, seed, (0,0,0), (5,5,5,5), (5,5,5,5))
    blur = cv2.medianBlur(foreground,5)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, threshold1=40, threshold2=300, apertureSize=3)
    dilation_size = 6
    dilation_type = cv2.MORPH_RECT
    kernel = cv2.getStructuringElement(
                dilation_type, (2 * dilation_size, 5 * dilation_size), 
                (dilation_size, dilation_size))
    closing = cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel, iterations=2)
    frame1, frame2 = filter(closing)
    return frame1, frame2


pic = cv2.imread('static/images/needle1.jpg')
contour_maker(pic)
  
    # cv2.imshow('gray', gray)
    # cv2.imshow('canny',canny)
    # cv2.imshow('closing',closing)
    # cv2.imshow('filtered',filtered)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()