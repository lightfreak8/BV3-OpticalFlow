# BV3 - FlowTrack
Optical Flow and Trajectory Estimator


## Overview
This program estimates trajectories by analizing consecutive frames using the concept of optical flow. It also allows a comparison between the estimated trajectories and the recorded GPS data. The GPS data, which is in GPX file format, is converted to UTM (Universal Transverse Mercator) coordinates for plotting purposes and accurate comparison.

## Features
- Extracts and saves individual frames from a video. (separate Python file)
- Converts geographic coordinates (latitude and longitude) from GPX files to UTM coordinates.
- Uses SIFT (Scale-Invariant Feature Transform) to detect and match features between consecutive frames.
- Plots GPS tracks and optical flow data for trajectory visualization.
- Enhances image contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization).
- Corrects lens distortion using intrinsic camera parameters.

## Prerequisites
- Python 3.10
- NumPy
- OpenCV 4.7.0
- Matplotlib
- gpxpy
- utm

## Procedure
- record a video and gps coordinates at the same time (e.g. App "GPS Logger")
- take several images from a chessboard
- process the chessboard images  by using `cameraCalibration.py` and save the camera parameters in a txt file
- adjust the paths in the script to point to your local directories
- run the script

## SW Helpies

### Camera Calibration

Requirements:\
    - camera with manual mode for setting exposure time, focus distance and ISO (sensitivity) manually\
    - chessboard with 6x9 squares or similiar

This calibration calculates parameters for the correction of images.
The camera matrix contains the values for focal length and optical centers. The camera matrix parameter values (intrinsic) as well as the found distortion coefficients can be used for removing distortion which is caused by the camera lens.
Whereas the extrinsic parameters (not needed) corresponds to rotation and translation vectors which translates the coordinates of a 3D point to a coordinate system.


Example parameters (which have to be saved in a file manually):
```
Camera matrix: 
1.75289881e+03 0.00000000e+00 5.48204571e+02
0.00000000e+00 1.75114882e+03 9.57329860e+02
0.00000000e+00 0.00000000e+00 1.00000000e+00

Distortion:
4.06432596e-02 -1.81478037e-01 -1.59435768e-03 1.78785960e-04 2.66227435e-01
```


### Frames Cutter
getFramesFromVideo.py

This program saves each frame from your provided video, allowing you to optimally set the parameters. This ensures that you get the optimum frame interval and image section for processing by FlowTrack later.

#### Description of adjustable parameters
- videoFPS = input video fps
- fpsDivider = depends from your desired fps rate for the extracted frames. \
  output fps = video fps / fps Divider\
  e.g. 30 fps / 5 = 6 fps
- resizedWidth and resizedHeight \
  It's important to provide a sufficient resolution. If the resolution is too low, FlowTrack may not find enough features, resulting in unsatisfactory tracking results.
- cropWidth, cropHeightBottom, cropHeightTop\
  Adjust the parameters if there are consistent elements in your image field, e.g. parts of your equipment (such as a car), or if a large part of the sky is visible.

Example:
```
videoFPS = 30 #input video fps
fpsDivider = 5 #fps divider

video_path = "C:/.../video"

resizedWidth = 1280
resizedHeight = 720

cropWidth = resizedWidth
cropHeightBottom = 200
cropHeightTop = 100
```

### GPX Plotter
gpxFilePlotter.py

This program visualizes your data from a GPX file. GPX files store GPS data as geographic latitude and longitude coordinates. To plot this data effectively, these coordinates are converted to UTM coordinates.

![Plot](GPX%20Plotter%20Map%20example%20black.png)

## How does it work in detail...
- initialize a plot with the starting point
- plot the recorded GPS coordinates from the GPX file
- load camera calibration parameters (if `cameraCalibration` is set to 1).
- for loop:
  - load image pair (frame before and current)
  - convert color image to grayscale (visualization with color frame)
  - correct images (if `cameraCalibration` is set to 1)
  - enhance contrast through clahe algorithm
  - calculate keypoints and descriptors through SIFT algorithm
  - match descriptors between previous and current frame
  - filter matches:
    - by comparing the distance ratio of the best match and the second best match for a specific feature
    - extract corresponding points into prev_points and next_points
    - filter points within ROI
    - calculate vector between previous and current point
    - extend the vector by a factor for increasing the accuracy
  - calculate the focus of expansion (FoE) point by using the mean of filtered_points + extended_vectors
  - compute the direction "left", "straight" or "right" based on the position of the FoE point
  - draw
    - ROI lines for visualization
    - lines and points between matching features
    - red point for FoE
  - put Text on visualization image with direction "left", "straight" or "right"
  - update map and calculate speed vector compontents and angle components (map update not visualized continuously)
- by pressing "ESC" finish script and visualize the updated trajectory on a plot


![hblalala](FLowTrack Map example black red.png)



