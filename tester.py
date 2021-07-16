import cv2 as cv
import numpy as np

from needle_class import NeedleBoy
from point_class import PointFinder

pic = cv.imread('static/images/needle1.jpg')

# tester = NeedleBoy(pic)
# tester.process()

tester = NeedleBoy(pic)