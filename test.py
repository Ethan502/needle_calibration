import cv2 as cv
import numpy as np

pic = cv.imread('static/images/needle2.jpg')

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


cv.imshow('pic', closing)
cv.waitKey()
cv.destroyAllWindows()

