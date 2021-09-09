import cv2 as cv
import numpy as np

pic = cv.imread('static/images/needle1.jpg')

print(pic.shape)

print(pic[556][486])

cv.circle(pic, (486,556), 1, (0,0,255),3)

cv.imshow("pic", pic)
cv.waitKey()
cv.destroyAllWindows()