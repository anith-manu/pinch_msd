import cv2
import time
import numpy as np
import handtrackingmodule as htm
import math
import zmq
from collections import deque
from scipy import signal

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


#####################################
wCam, hCam = 640, 480
#####################################

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

volBar = 0
volPer = 0


detector = htm.handDetector(detectionCon=0.7)

history_length = 16
point_history_x = deque(maxlen=history_length)
point_history_y = deque(maxlen=history_length)


point_list = [5, 9, 13, 17]

while True:

    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        x1, y1, z1 = lmList[4][1],lmList[4][2], lmList[4][3]
        x2, y2, z2 = lmList[8][1], lmList[8][2], lmList[8][3]

        x0, y0, z0 = lmList[0][1], lmList[0][2], lmList[0][3]

        cx,cy = (x1+x2)//2, (y1+y2)//2

        avg_z = (z1 + z2)/2

        threshold_z = 0.1

        if avg_z < threshold_z:
            noise_sigma = (threshold_z - avg_z) * 200
            noise = np.random.normal(0, noise_sigma, 4)
            x1 = int(x1 + noise[0])
            y1 = int(y1 + noise[1])

            x2 = int(x2 + noise[2])
            y2 = int(y2 + noise[3])

            x0 = int(x0 + noise[2])
            y0 = int(y0 + noise[3])
            
        else: 
            x1 = int(x1)
            y1 = int(y1)

            x2 = int(x2)
            y2 = int(y2)

            x0 = int(x0)
            y0 = int(y0)

        
        point_history_x.append(x0)
        point_history_y.append(y0)
     

        cv2.circle(img, (x1,y1), 15, (255,0,255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x0, y0), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1,y1), (x2,y2),(255,0,255),3)
        # cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)

        for i in point_list:
            x, y = lmList[i][1],lmList[i][2]
            



        if len(point_history_x) == 16:
            x3_mean_disturbance = np.mean(np.abs(signal.savgol_filter(point_history_x, window_length=7, polyorder=2, deriv=1)))
            y3_mean_disturbance = np.mean(np.abs(signal.savgol_filter(point_history_y, window_length=7, polyorder=2, deriv=1)))
            mean_disturbance = (x3_mean_disturbance+y3_mean_disturbance)/2
            print(mean_disturbance)
        # if length<50: 
        #     cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

            if mean_disturbance < 1:
                result =  str(length) 
                result = result.encode("utf-8")

                message = socket.recv()
                socket.send(result)
        
       

        # print(length)


    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    # cv2.putText(img,f'FPS:{int(fps)}',(40,50), cv2.FONT_HERSHEY_COMPLEX,
    #             1, (255,0,0),3)

    cv2.imshow("Img", cv2.flip(img, 1))
    cv2.waitKey(1)
