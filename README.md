Auto-Calibration program for single-cell proteomics microscopes.

This program is written to help shorten the long and human-dependant procress of calibrating the very fine tipped microscopes that are used.

Using Python OpenCV, this program uses computervision to interpret photos recieved from a needle tip camera, and then find the center calibration point as well as the tip-points of any needles in focus. Either the one needle is in focus, or the needle and its reflection in the well-plate are found. Using the tip-points of both the needle and the reflection help to move and calibrate the needle in three dimensional space.

The program works even if one of the needles or the calibration point are out of focus, so long as there is at least one needle in view, which there always should be thanks to the tip camera. 

main.py will run the entire program, or the flask app can be used. Or simply call the 'process' funciton of the CalibrationPoints class, passing in the image as the only parameter. 