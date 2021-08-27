import cv2 as cv
import numpy as np

pic = cv.imread('static/images/needle2.jpg')
lower_range = np.array([0,0,0])
upper_range = np.array([85,85,85])

hsv = cv.cvtColor(pic, cv.COLOR_BGR2HSV)
mask = cv.inRange(hsv, lower_range, upper_range)
contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
backdrop = np.zeros_like(mask)
for i, c in enumerate(contours):
    area = cv.contourArea(c)
    if 1100 <= area <= 2000:
        cv.drawContours(backdrop, contours, i, [255,255,255], cv.FILLED)



contours, _ = cv.findContours(backdrop, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
if len(contours) > 0:
    cnt = contours[-1]
    left =  tuple(cnt[cnt[:,:,0].argmin()][0])
    top = tuple(cnt[cnt[:,:,1].argmin()][0])
    bottom = tuple(cnt[cnt[:,:,1].argmax()][0])
    right = tuple(cnt[cnt[:,:,0].argmax()][0])


top_x, top_y = top[0], top[1]
bottom_x, bottom_y = bottom[0], bottom[1]
left_x, left_y = left[0], left[1]
right_x, right_y = right[0], right[1]

center_x = ((right_x - left_x)/2) + left_x
center_y = ((bottom_y - top_y)/2) + top_y
center_point = (round(center_x),round(center_y))
point = center_point

cv.circle(pic, point, 2, (255, 0, 0), 2)


cv.imshow('pic', pic)
cv.waitKey()
cv.destroyAllWindows()

