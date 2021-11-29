import torch
import numpy as np
import cv2 as cv
import time



# Model
model = torch.hub.load('ultralytics/yolov5', 'yolov5n')

t = 0
isDetected = False
count_time = 0
confidence = 0

# fourcc = cv.VideoWriter_fourcc(*'MP4V')
fourcc = cv.VideoWriter_fourcc(*'XVID')



cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # print(frame.shape)
    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    if isDetected:
        if time.time() - t < 5:
            print(time.time()-t)
            recorder.write(frame)
            cv.imshow('frame', frame)
            if cv.waitKey(1) == ord('q'):
                break
            continue
        # else:
        #     recorder.release()
            
    # detection
    results = model(frame)
    result_list = results.display(crop=True)
    for i in range(len(result_list)):
        print(result_list[i]['label'])
        if str.split(result_list[i]['label'])[0] == 'person':
            confidence += 1
        else:
            isDetected = False
            confidence = 0

    if confidence >=4:
        print('hit')
        t = time.time()
        isDetected = True
        count_time += 1
        name = 'detected%d.avi' % (count_time)
        recorder = cv.VideoWriter(name,fourcc, 20.0, (640,480))
        recorder.write(frame)

    cv.imshow('frame', frame)
    if cv.waitKey(1) == ord('q'):
        break




# When everything done, release the capture
recorder.release()
cap.release()
cv.destroyAllWindows()
