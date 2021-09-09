from finder_class import CalibrationPoints
import cv2 as cv

pic = cv.imread('static/images/needle3.jpg')

point = CalibrationPoints(pic)
point.process()

right_needle_point = point.rightpoint
left_needle_point = point.leftpoint
calibration_point = point.calib_point

print(f"This is the point on the left side {left_needle_point}")
print(f"This is the point on the right side {right_needle_point}")
print(f"This is the center circle point {calibration_point}")
