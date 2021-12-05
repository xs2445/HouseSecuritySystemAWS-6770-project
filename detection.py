import torch
import numpy as np
import cv2 as cv
import time
import datetime
from UploadAWS import upload_file, upload_file2
import threading
import boto3
from ImageDetection import compare_faces


# the length of the video as seconds
VIDEO_LENGTH = 5

# the time interval between two frames
TIME_INTERVAL = 1e-1

# FPS
FPS = 1/TIME_INTERVAL

# the number of frames in the video
VIDEO_FRAME = VIDEO_LENGTH // TIME_INTERVAL

# video encoding format
FOURCC = cv.VideoWriter_fourcc(*'XVID')

# size of frames in the video, depends on the camera
RESOLUTION = (640,480)


def run():
    """
    The main thread for detection and uploading detected videos.
    """

    # s3_client = boto3.resource('s3')
    s3_client = boto3.client('s3')

    # visual detecting model - yolov5 nano version
    model = torch.hub.load('ultralytics/yolov5', 'yolov5n')

    # denotes wether to record video or detect for person
    isDetected = False
    # the time class person is detected
    confidence = 0
    # frame counter 
    frames_count = 0

    # assign camera
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    while True:
        # wait for a while
        time.sleep(TIME_INTERVAL = 1e-1)
        # Capture frame-by-frame from camera
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        # start recording if class person is detected
        if isDetected:
            # record a 50 frames video
            if frames_count < VIDEO_FRAME:
                # frame counter
                frames_count += 1
                # write one frame to the video
                recorder.write(frame)
                # show the frame
                cv.imshow('frame', frame)
                # quit the program if "q" is typed
                if cv.waitKey(1) == ord('q'):
                    print('Video saved as %s' % (name))
                    break
                continue
            else:
                print('Video saved as %s' % (name))
                upload_file2(s3_client, name, '6770-project')
                isDetected = False
                
        # detection and classification
        results = model(frame)
        # save all the result in a list
        result_list = results.display(crop=True)

        # check if person is detected
        for i in range(len(result_list)):
            # print the class of detected object
            print(result_list[i]['label'])
            if str.split(result_list[i]['label'])[0] == 'person':
                confidence += 1
                break
            else:
                isDetected = False
                confidence = 0

        # only when person is detected for more than 4 continuous times, record the video.
        if confidence >=4:
            # confident enough that a person is detected
            print('Hit!')
            # start recording from the next iteration
            isDetected = True
            # put frame counter to 0
            frames_count = 0
            # count_time += 1
            name = 'vids/' + datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S") + '_vid.avi'
            # name = 'vids/' + datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S") + '.mp4'
            name_pic = name[:-7] + 'pic.jpg'
            # write the captured image for further analysis
            cv.imwrite(name_pic, frame)
            # upload the frame to the cloud
            upload_file2(s3_client, name_pic, '6770-project')
            # start recording the video
            recorder = cv.VideoWriter(name, FOURCC, FPS, RESOLUTION)
            recorder.write(frame)
            print('Recording...')

        cv.imshow('frame', frame)
        if cv.waitKey(1) == ord('q'):
            break

    # When everything done, release the capture
    recorder.release()
    cap.release()
    cv.destroyAllWindows()


if __name__ == '__main__':
    run()