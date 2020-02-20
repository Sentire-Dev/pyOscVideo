#!/usr/bin/env python

import numpy as np
import cv2

cap = cv2.VideoCapture(0)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define the codec and create VideoWriter object
#fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#out = cv2.VideoWriter('output2.mpeg4',fourcc, 20.0, (w,h))

while(cap.isOpened()):
    #print([w, h])
    #print('opened')
    print("frame rate: " + str(cap.get(cv2.CAP_PROP_FPS)))
    ret, frame = cap.read()
    print('ret: ' + str(ret))
    if ret==True:
        print('reading')
        frame = cv2.flip(frame,0)

        # write the flipped frame
        out.write(frame)

        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()
