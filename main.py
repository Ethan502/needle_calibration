from finder_class import CalibrationPoints
import cv2 as cv

pic = cv.imread('static/images/needle1.jpg')

point = CalibrationPoints(pic)
point.process()

right_needle_point = point.rightpoint
left_needle_point = point.leftpoint
calibration_point = point.calib_point
