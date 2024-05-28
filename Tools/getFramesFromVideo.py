"""
cut a video and save frames with specified fps rate and resolution
adjust the parameters for the output image size
"""



videoFPS = 30 #input video fps
fpsDivider = 5 #fps divider

video_path = "C:/Users/rapha/switchdrive/PHO_Studium/Bildverarbeitung 3/SEMESTERPROJEKT/Aufnahmen_09.05.2024/chur_7_t2.mp4"
output_folder = "C:/Users/rapha/switchdrive/PHO_Studium/Bildverarbeitung 3/SEMESTERPROJEKT/Aufnahmen_09.05.2024/video7t2"

resizedWidth = 1280
resizedHeight = 720

cropWidth = resizedWidth
cropHeightBottom = 200
cropHeightTop = 100


#%%
import cv2
import os


def extract_frames(videoFPS, fpsDivider, video_path, output_folder, resizedWidth, resizedHeight, cropWidth, cropHeightBottom, cropHeightTop):
    
    # Check whether the output folder exists, otherwise create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # open the video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Video could not be loaded")
        return

    frame_count = 0
    saved_frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        resized_frame = cv2.resize(frame, (resizedWidth, resizedHeight), interpolation= cv2.INTER_LINEAR)
        cropped_image = resized_frame[cropHeightBottom:resizedHeight-cropHeightTop,0:cropWidth]
        croppedHeight, croppedWidth, c = cropped_image.shape

        gray = cropped_image
        frame_count += 1

        # extract every xth frame
        if frame_count % fpsDivider == 0:
            output_file = os.path.join(output_folder, f"{saved_frame_count+1:04d}.jpg")
            #gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY) #optional
            cv2.imwrite(output_file, gray)
            saved_frame_count += 1

    cap.release()
    print(f"Finished! {saved_frame_count} frames were extracted and saved")
    outputFPS = videoFPS / fpsDivider
    print(f"Every {fpsDivider} frame was cutted -> destination fps = {outputFPS}")
    print(f"Resolution {croppedHeight} * {croppedWidth}")


if __name__ == "__main__":
    
    print("extracting started...")
    extract_frames(videoFPS, fpsDivider, video_path, output_folder, resizedWidth, resizedHeight, cropWidth, cropHeightBottom, cropHeightTop)
