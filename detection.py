import torch
import numpy as np
import cv2 as cv
import time
import datetime
from UploadAWS import upload_file, upload_file2
import threading
import boto3
from ImageDetection import compare_faces


def run():
    """
    The main thread for detection and uploading detected videos.
    """

    # s3_client = boto3.resource('s3')
    s3_client = boto3.client('s3')

    # Model
    model = torch.hub.load('ultralytics/yolov5', 'yolov5n')

    t = 0
    isDetected = False
    count_time = 0
    confidence = 0

    # fourcc = cv.VideoWriter_fourcc(*'MP4V')
    # fourcc = 0x7634706d
    # fourcc = cv.VideoWriter_fourcc(*'X264')
    # fourcc = cv.VideoWriter_fourcc(*'avc1')
    fourcc = cv.VideoWriter_fourcc(*'H264')
    # fourcc = 0x31637661
    # fourcc = cv.VideoWriter_fourcc('a','v','c','1')
    # print(fourcc)
    # fourcc = cv.VideoWriter_fourcc(*'XVID')

    # assign camera
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    while True:
        time.sleep(1e-1)
        # Capture frame-by-frame from camera
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        if isDetected:
            # record a 5 seconds video
            if time.time() - t < 5:
                recorder.write(frame)
                cv.imshow('frame', frame)
                if cv.waitKey(1) == ord('q'):
                    print('Saved as %s' % (name))
                    break
                continue
            else:
                print('Saved as %s' % (name))
                upload_file2(s3_client, name, '6770-project')
                isDetected = False
                
        # detection and classification
        results = model(frame)
        result_list = results.display(crop=True)

        # check if person is detected
        for i in range(len(result_list)):
            print(result_list[i]['label'])
            if str.split(result_list[i]['label'])[0] == 'person':
                confidence += 1
                break
            else:
                isDetected = False
                confidence = 0

        # only when person is detected for more than 4 continuous times, record the video.
        if confidence >=4:
            print('Hit!')
            t = time.time()
            isDetected = True
            count_time += 1
            # name = 'vids/' + datetime.datetime.now().strftime("%m-%d-%Y-%H-%M-%S") + '.avi'
            name = 'vids/' + datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S") + '.mp4'
            name_pic = name[:-4]+'.jpg'
            print(name_pic)
            cv.imwrite(name_pic, frame)
            recorder = cv.VideoWriter(name, fourcc, 10.0, (640,480))
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