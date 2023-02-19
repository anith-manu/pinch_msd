import cv2
import time
import numpy as np
import handtrackingmodule as htm
import math
import zmq
from collections import deque
from scipy import signal
import sys

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

history_length = 21
point_history_x5 = deque(maxlen=history_length)
point_history_y5 = deque(maxlen=history_length)

point_history_x9 = deque(maxlen=history_length)
point_history_y9 = deque(maxlen=history_length)

point_history_x13 = deque(maxlen=history_length)
point_history_y13 = deque(maxlen=history_length)

point_history_x17 = deque(maxlen=history_length)
point_history_y17 = deque(maxlen=history_length)


point_list = [5, 9, 13, 17]

while True:

    success, img = cap.read()
    img = detector.findHands(img, draw=False)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
    

        z1 = lmList[16][3]
        z2 = lmList[20][3]

        avg_z = -(z1 + z2)/2
      

    

        for i in range(len(lmList)):
            x, y = lmList[i][1],lmList[i][2]

            noise_sigma = pow(10, (20*avg_z)+1.65) 
             
            noise = np.random.normal(0, noise_sigma, 4)

            x = int(x + noise[0])
            y = int(y + noise[0])


            cv2.circle(img, (x,y), 5, (0,0,255), cv2.FILLED)
           
            
            if i == 4:
                x1, y1 = x, y
            if i == 8:
                x2, y2 = x, y
                cv2.line(img, (x1,y1), (x2,y2),(0,255,0),3)
                length = math.hypot(x2 - x1, y2 - y1)
                # result =  str(length) 
                # result = result.encode("utf-8")

                # message = socket.recv()
                # socket.send(result)
            
            if i == 5:
                point_history_x5.append(x)
                point_history_y5.append(y)
            elif i == 9:
                point_history_x9.append(x)
                point_history_y9.append(y)
            elif i == 13:
                point_history_x13.append(x)
                point_history_y13.append(y)
            elif i == 17:
                point_history_x17.append(x)
                point_history_y17.append(y)




    
       
        if len(point_history_y17) == 21 :
            x5_mean_disturbance = np.mean(np.abs(signal.savgol_filter(point_history_x5, window_length=7, polyorder=3, deriv=2)))
            y5_mean_disturbance = np.mean(np.abs(signal.savgol_filter(point_history_y5, window_length=7, polyorder=3, deriv=2)))

            x9_mean_disturbance = np.mean(np.abs(signal.savgol_filter(point_history_x9, window_length=7, polyorder=3, deriv=2)))
            y9_mean_disturbance = np.mean(np.abs(signal.savgol_filter(point_history_y9, window_length=7, polyorder=3, deriv=2)))

            x13_mean_disturbance = np.mean(np.abs(signal.savgol_filter(point_history_x13, window_length=7, polyorder=3, deriv=2)))
            y13_mean_disturbance = np.mean(np.abs(signal.savgol_filter(point_history_y13, window_length=7, polyorder=3, deriv=2)))

            x17_mean_disturbance = np.mean(np.abs(signal.savgol_filter(point_history_x17, window_length=7, polyorder=3, deriv=2)))
            y17_mean_disturbance = np.mean(np.abs(signal.savgol_filter(point_history_y17, window_length=7, polyorder=3, deriv=2)))

            mean_disturbance = (x5_mean_disturbance+y5_mean_disturbance+ x9_mean_disturbance+y9_mean_disturbance+ 
                                x13_mean_disturbance+y13_mean_disturbance+ x17_mean_disturbance+y17_mean_disturbance)/8


            if mean_disturbance < 1:
                result =  str(length) 
                result = result.encode("utf-8")

                message = socket.recv()
                socket.send(result)


    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    # cv2.putText(img,f'FPS:{int(fps)}',(40,50), cv2.FONT_HERSHEY_COMPLEX,
    #             1, (255,0,0),3)

    cv2.imshow("Img", cv2.flip(img, 1))
    cv2.waitKey(1)
