from finder_class import PointFinder
import cv2 as cv

pic = cv.imread('static/images/needle1.jpg')

point = PointFinder(pic)
point.process()