"""
cameraCalibration



This calibration calculates parameters for the correction of images.
The camera matrix contains the values for focal length and optical centers. The camera matrix parameter values (intrinsic) as well as the found distortion coefficients can be used for removing distortion which is caused by the camera lens.
Whereas the extrinsic parameters corresponds to rotation and translation vectors which translates the coordinates of a 3D point to a coordinate system.




The calculated camera parameters are not saved automatically and have to be copied from the console and saved in a txt file.

Requirements:
    - camera with manual mode for setting exposure time, focus distance and ISO (sensitivity) manually
    - chessboard with (6, 9) squares or adjusted amount of squares
    

with help of https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html
"""

chessboardImg_path = 'C:/Users/rapha/switchdrive/PHO_Studium/Bildverarbeitung 3/SEMESTERPROJEKT/Camera Calib Chessboard/chessboard_images/*.jpg'

# define the dimensions of checkerboard
CHECKERBOARD = (6,9) #amount of squares


import cv2
import numpy as np
import os
import glob
 

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
 
# vector to store vectors of 3D points for each checkerboard image
objpoints = []
# vector to store vectors of 2D points for each checkerboard image
imgpoints = [] 
 
 
# Defining world coordinates for 3D points
objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)
prev_img_shape = None
 
# Extracting path of individual image stored in a given directory
images = glob.glob(chessboardImg_path)
saved_image_counter = 1
for fname in images:
   
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    # Find the chess board corners
    # If desired number of corners are found in the image then ret = true
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
     
    
    #If desired number of corner are detected, we refine the pixel coordinates and display them on the images of checker board
    if ret == True:
        objpoints.append(objp)
        # refining pixel coordinates for given 2d points.
        corners2 = cv2.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria)
         
        imgpoints.append(corners2)
 
        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, CHECKERBOARD, corners2, ret)
        
    image_name = os.path.join("chessboard_images/calibration", f"image{saved_image_counter}.jpg")
    saved_image_counter += 1
    cv2.imwrite(image_name, img)
    cv2.imshow(image_name,img)
    cv2.waitKey(0)
    
 
cv2.destroyAllWindows()
 
h,w = img.shape[:2]
 
"""
Performing camera calibration by passing the value of known 3D points (objpoints)
and corresponding pixel coordinates of the detected corners (imgpoints)
"""
ret, cmtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
 
print("Camera matrix : \n")
print(cmtx)
print("dist : \n")
print(dist)
# print("rvecs : \n")
# print(rvecs)
# print("tvecs : \n")
# print(tvecs)