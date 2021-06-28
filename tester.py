import cv2 as cv
import numpy as np

from needle_class import NeedleBoy

pic = cv.imread('static/images/needle1.jpg')

tester = NeedleBoy(pic)
tester.process()