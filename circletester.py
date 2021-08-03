import cv2 as cv
import numpy as np

img = cv.imread('static/images/needle1.jpg') #read the image

def area_bandpass_filter(img):
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
            #new_frame = cv.bitwise_or(new_frame, mask)
    print(count)
    return mask

def center_point_finder(img):
    """finds the center point of the detected circle

    Args:
        img ([nd.array]): [b/w mask of just the detected center point]
    """

    contours = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    # cv.imshow('circle', img)
    # cv.waitKey()
    # cv.destroyAllWindows()


lighter_img = np.maximum(img, 10)
foreground = lighter_img.copy()
seed = (10,10) # using the top left corner as the "background" seed color
cv.floodFill(foreground, None, seedPoint=seed, newVal=(0,0,0), loDiff=(5,5,5,5), upDiff=(5,5,5,5))
gray = cv.cvtColor(foreground, cv.COLOR_BGR2GRAY)
thresh = cv.threshold(gray, 1, 255, cv.THRESH_BINARY)[1]
thresh = cv.morphologyEx(thresh, cv.MORPH_OPEN, cv.getStructuringElement(cv.MORPH_RECT, (5,5)))
filtered = area_bandpass_filter(thresh)
circle = center_point_finder(filtered)






cv.imshow('og', img)
cv.imshow('lighter', lighter_img)
cv.imshow('foreground', foreground)
cv.imshow('gray', gray)
cv.imshow('thresh', thresh)
cv.imshow('filtered', filtered)
cv.waitKey()
cv.destroyAllWindows()

