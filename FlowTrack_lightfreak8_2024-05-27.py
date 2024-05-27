"""
FlowTrack 

Optical Flow and Trajectory Estimator

Note: The plot isn't updated automatically - only once in the end. To update the plot continuously, uncomment "#plt.draw()" at the end of the script.

Author: Raphael Krause
Date: 2024-05-27

"""

#%% Libraries
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
import gpxpy
import utm

#%% Paths
#images
folder_path = "C:/Users/rapha/switchdrive/PHO_Studium/Bildverarbeitung 3/SEMESTERPROJEKT/Aufnahmen_09.05.2024/imagesFlowTrack"
#gpx file
gpx_path = "C:/Users/rapha/switchdrive/PHO_Studium/Bildverarbeitung 3/SEMESTERPROJEKT/Aufnahmen_09.05.2024/gpsFlowTrack.gpx"
# camera calibration parameter 
intrinsic_path = "C:/Users/rapha/switchdrive/PHO_Studium/Bildverarbeitung 3/SEMESTERPROJEKT/Aufnahmen_09.05.2024/intrinsic.txt"
cameraCalibration =1 #1 = load intrinsic parameters if images aren't corrected


#%% Default values
angle = 112 #start alignment map
x, y = 0, 0 #starting point on map
xCenterArea = 120 # tolerance image range x-axis


plt.close('all')

#%% functions

#convert geographic coordinates (latitude and longitude) to UTM coordinates (eastings and northings)
def convert_to_meters(lat, lon, start_lat, start_lon):
    utm_coords = utm.from_latlon(lat, lon)
    start_utm_coords = utm.from_latlon(start_lat, start_lon)
    return utm_coords[0] - start_utm_coords[0], utm_coords[1] - start_utm_coords[1]


def plot_gpx(gpx_file, ax):
    # load gpx file
    with open(gpx_file, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    # extract GPS data and convert to metres
    latitudes = []
    longitudes = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                latitudes.append(point.latitude)
                longitudes.append(point.longitude)

    start_lat, start_lon = latitudes[0], longitudes[0]
    latitudes.reverse()
    longitudes.reverse()
    latitudes_meters = []
    longitudes_meters = []

    for lat, lon in zip(latitudes, longitudes):
        x, y = convert_to_meters(lat, lon, start_lat, start_lon)
        latitudes_meters.append(x)
        longitudes_meters.append(y)

    #plot
    ax.plot(longitudes_meters, [-y for y in latitudes_meters], color='k', linewidth=1, label='GPS Track')
    ax.set_xlabel('X [m]')
    ax.set_ylabel('Y [m]')
    ax.set_title('GPX Track and Optical Flow Plot')
    ax.grid(True)
    ax.axis('equal')  #ensures axis ratio
    ax.legend()

#Reads camera intrinsic parameters from a file.
def read_camera_parameters(intrinsic_path_l):
    inf = open(intrinsic_path_l, 'r')
    cmtx = []
    dist = []
    # Ignore first line
    line = inf.readline()
    for _ in range(3):
        line = inf.readline().split()
        line = [float(en) for en in line]
        cmtx.append(line)
    # Ignore line that says "distortion"
    line = inf.readline()
    line = inf.readline().split()
    line = [float(en) for en in line]
    dist.append(line)

    # cmtx = camera matrix, dist = distortion parameters
    return np.array(cmtx),np.array(dist)

#init map
def draw_map_init():
    plt.xlabel('X (meters)') 
    plt.ylabel('Y (meters)')
    plt.title('GPS Track and Optical Flow Plot')
    ax = plt.gca()
    ax.scatter(0, 0, color='red')  # start point
    ax.set_aspect('equal', adjustable='box')  # equal axis ratio
    return ax


# plot the estimated point taking into account speed and degree of the curvature.
# converts angle into x and y displacements by sine and cosine to correctly display the direction of movement on the map
def draw_map_update(ax, x,y, direction,shift, angle, vectorLength):
    # Create a linear function to estimate the angle of a curve depending on the degree of curvature
    angleMax = 4.4
    shiftMax = 600
    m = angleMax/shiftMax
    angle_change = shift * m
    #print(f"angle change: {angle_change}")
    
    global factor_x
    global factor_y
    
    if direction == "straight":
        # create a linear function to estimate the speed by considering the mean vector length
        speedMax = 1
        vectorLengthMaxX = 22
        vectorLengthMaxY = 30
        m2X = speedMax/vectorLengthMaxX
        m2Y = speedMax/vectorLengthMaxY
        factor_x = vectorLength * m2X
        factor_y = vectorLength * m2Y
        dx, dy = np.cos(np.radians(angle)) * factor_x, np.sin(np.radians(angle) * factor_y)
        #print(f"{dx:.2f}, {dy:.2f}")
        
    elif direction == "right":
        factor_x = 1
        factor_y=1
        # subtract angle_change to angle before
        angle -= angle_change
        dx, dy = np.cos(np.radians(angle)) * factor_x, np.sin(np.radians(angle) * factor_y)
    elif direction == "left":
        factor_x = 1
        factor_y=1
        # add angle_change to angle before
        angle += angle_change
        dx, dy = np.cos(np.radians(angle)) * factor_x, np.sin(np.radians(angle) * factor_y)
        
    ax.scatter(x,y, s= 10, color = 'red', marker = '.')
    #add the calculated dx and dy component to the values from before
    x, y = x+dx, y+dy
    plt.gca().set_aspect('equal', adjustable='box') #ensures axis ratio
    return angle,x,y
    

def enhance_contrast_clahe(img):
    if len(img.shape) == 3:  #check if image has 3 channels = color image
        # convert image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img  # already gray scale image
    
    # apply CLAHE algorithm
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    clahe_img = clahe.apply(gray)
    #cv2.imshow("gray", clahe_img)
    #print(f" mean: {cv2.mean(clahe_img)}")
    return clahe_img


#%% init
#init map with start point
ax = draw_map_init()
#plot gps coordinates from gpx file
plot_gpx(gpx_path, ax)

# init SIFT
sift = cv2.SIFT_create()

# sort images
image_files = sorted([os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(('.jpg', '.jpeg', '.png'))])
# amount of images in folder
num_images = len(image_files)

#load first image
frame = cv2.imread(image_files[0])
# get image size
height, width, c = frame.shape
xCenterPixel = int(width/2) # centerpoint x-axis
#print(f"xCenterPixel {xCenterPixel}")
# define ROI
xCenterAreaLeft = xCenterPixel - xCenterArea
xCenterAreaRight = xCenterPixel + xCenterArea


print("init")

#load camera calibration
if cameraCalibration:
    cmtx, dist = read_camera_parameters(intrinsic_path)
    # Corrects the distortion thru the camera calibration
    new_cmtx, _ = cv2.getOptimalNewCameraMatrix(cmtx, dist, (width, height), 1, (width, height))

intersection_point_before = None
shift = 0 # along x-axis

#%% main loop
for i in range(num_images - 1):
    
    print(f"img{i}")
  
    # load consecutive images
    prev_frame = cv2.imread(image_files[i])
    current_frame = cv2.imread(image_files[i + 1])
    
    if cameraCalibration:
        # corrects the distortion thru the camera calibration
        prev_frame = cv2.undistort(prev_frame, cmtx, dist, None, new_cmtx)
        current_frame = cv2.undistort(current_frame, cmtx, dist, None, new_cmtx)
    
    # convert images to grayscale
    prev_gray= enhance_contrast_clahe(prev_frame)
    current_gray = enhance_contrast_clahe(current_frame)

    # calc SIFT-features and descriptors
    prev_keypoints, prev_descriptors = sift.detectAndCompute(prev_gray, None)
    current_keypoints, current_descriptors = sift.detectAndCompute(current_gray, None)
    
    # match SIFT-features
    # compare images and find the best matches
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(prev_descriptors, current_descriptors, k=2) #k = amount of matchings

    # filter good matches using the distance ratio of the best and second-best match
    good_matches = []
    prev_point = None 
    for m, n in matches:
        if m.distance < 0.2 * n.distance:
            good_matches.append(m)
            #print(f"good matches: {len(good_matches)}")

    # extract corresponding points
    prev_points = np.float32([prev_keypoints[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    next_points = np.float32([current_keypoints[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        
    # calculate the extension vectors only for points within ROI and filter points
    # save the filtered points seperately
    filtered_points = []
    extended_vectors = []
    speed_vectors = []
    for prev_point, next_point in zip(prev_points, next_points):
        if xCenterAreaLeft <= next_point[0, 0] <= xCenterAreaRight:
            vector = next_point - prev_point
            #print(f"vector {vector}")
            speed_vectors.append(vector)
            vector[:, 0] *= 10  # Extend the vector by a factor of 10 for increasing the precision
            vector[:, 1] *= 10
            extended_vectors.append(vector)
            filtered_points.append(next_point)       
    extended_vectors = np.array(extended_vectors)
    
    #check whether at least one vector is present
    if len(extended_vectors) < 1:
        continue
    else:
        # calc focus of expansion point within filtered vectors list
        intersection_point = np.mean(filtered_points + extended_vectors, axis=0).astype(int)
        #print(f" intersec. point: {intersection_point[0,0]}")
    
    #check validity of intersection point
    if (np.abs(intersection_point[0, 0]) > 10000) or (np.abs(intersection_point[0, 1]) > 10000):
        # jump back to loop start
        print("intersection_point is not valid")
        continue
    
    # compute the direction based on the position of focus of expansion point
    if intersection_point[0, 0] < xCenterAreaLeft:
        direction = "right"
        shift = np.abs(xCenterAreaLeft - intersection_point[0,0])  
        #print(f"shift r: {shift} pixels")
        speedMeanVector=1

    elif intersection_point[0, 0] > xCenterAreaRight:
        direction = "left"
        shift = np.abs(xCenterAreaRight - intersection_point[0,0])
        #print(f"shift l: {shift} pixels")
        speedMeanVector=1

    else:
        direction = "straight" 
        shift = 0
        speedMeanVector = np.mean(np.abs(speed_vectors))
        print(f"speed: {speedMeanVector:.1f}")


    #draw xCenterArea lines  
    cv2.line(prev_frame, (xCenterPixel+xCenterArea, 0), (xCenterPixel + xCenterArea, height), (255, 255, 255), 1)
    cv2.line(prev_frame, (xCenterPixel-xCenterArea, 0), (xCenterPixel - xCenterArea, height), (255, 255, 255), 1)
    
    # Draw lines between matching features
    for prev_point, next_point in zip(prev_points, next_points):
        x1, y1 = prev_point.ravel()
        x2, y2 = next_point.ravel()
        
        cv2.line(prev_frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2) #green connection vector line
        cv2.circle(prev_frame, (int(x1), int(y1)), 5, (255, 0, 0), -1) #blue previous image
        cv2.circle(prev_frame, (int(x2), int(y2)), 5, (0, 255, 0), -1) #green current image

    # Mark the focus of expansion point
    cv2.circle(prev_frame, (intersection_point[0, 0], intersection_point[0, 1]), 10, (0, 0, 255), -1)

    # Show the updated image with direction
    cv2.putText(prev_frame, direction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    cv2.imshow("Optical Flow", prev_frame)    
    # draw map
    angle, x, y = draw_map_update(ax, x,y, direction, shift, angle, speedMeanVector)
    #plt.draw() #uncomment for constantly updating the plot

    #%% End of Program Process key input
    key = cv2.waitKey(1)
    if key == 27:  # ESC to 
        plt.draw()
        break
cv2.destroyAllWindows()