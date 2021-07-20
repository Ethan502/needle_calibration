import cv2
import numpy as np

pic = cv2.imread('static/images/needle1.jpg')

pic = np.maximum(pic, 10)

foreground = pic.copy()

seed = (10,10)

cv2.floodFill(foreground, None, seed, (0,0,0), (5,5,5,5), (5,5,5,5))

gray = cv2.cvtColor(foreground, cv2.COLOR_BGR2GRAY)

thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (5,5)))

cv2.imshow('foreground', foreground)
cv2.imshow('gray',gray)
cv2.imshow('thresh', thresh)
cv2.imshow('pic',pic)

cv2.waitKey(0)
cv2.destroyAllWindows()
