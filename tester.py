import cv2 as cv
import numpy as np

pic = cv.imread('static/images/needle1.jpg')

while True:
    img = pic.copy()

    clahefilter = cv.createCLAHE(clipLimit=2.0, tileGridSize=(16,16))


    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    GLARE_MIN = np.array([0,0,50], np.uint8)
    GLARE_MAX = np.array([0,0,255],np.uint8)

    hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    #hsv
    frame_threshold = cv.inRange(hsv_img, GLARE_MIN, GLARE_MAX)

    #inpaint - this
    mask1 = cv.threshold(gray, 220, 255, cv.THRESH_BINARY)[1]
    result1 = cv.inpaint(img, mask1, 0.1, cv.INPAINT_TELEA)

    #clahe
    claheFrame = clahefilter.apply(gray)

    #color - this
    lab = cv.cvtColor(img, cv.COLOR_BGR2LAB)
    lab_planes = cv.split(lab)
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    lab_planes[0] = clahe.apply(lab_planes[0])
    lab = cv.merge(lab_planes)
    clahe_bgr = cv.cvtColor(lab, cv.COLOR_LAB2BGR)

    #inpaint + hsv
    result = cv.inpaint(img, frame_threshold, 0.1, cv.INPAINT_TELEA)

    #inpaint + clahe
    gray1 = cv.cvtColor(clahe_bgr, cv.COLOR_BGR2GRAY)
    mask2 = cv.threshold(gray1, 220, 255, cv.THRESH_BINARY)[0]
   # result2 = cv.inpaint(img, mask2, 0.1, cv.INPAINT_TELEA)


    # this
    #hsv + inpaint + clahe
    lab1 = cv.cvtColor(result, cv.COLOR_BGR2LAB)
    lab_planes1 = cv.split(lab1)
    clahe1 = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    lab_planes1[0] = clahe1.apply(lab_planes1[0])
    lab1 = cv.merge(lab_planes1)
    clahe_bgr1 = cv.cvtColor(lab1, cv.COLOR_LAB2BGR)

    cv.imshow("IMAGE", img)
    cv.imshow("GRAY", gray)
    cv.imshow("HSV", frame_threshold)
    cv.imshow("CLAHE", clahe_bgr)
    cv.imshow("LAB", lab)
    cv.imshow("HSV + INPAINT", result)
    cv.imshow("INPAINT", result1)
    #cv.imshow("CLAHE + INPAINT", result2)  
    cv.imshow("HSV + INPAINT + CLAHE   ", clahe_bgr1)

    if cv.waitKey(1) == ord('q'):
        break

cv.destroyAllWindows()

