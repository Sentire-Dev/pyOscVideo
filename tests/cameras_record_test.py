"""
    TODO: add file description
"""

# ******************************************************************************
#  Copyright (c) 2020. Pascal Staudt, Bruno Gola                               *
#                                                                              *
#  This file is part of pyOscVideo.                                            *
#                                                                              *
#  pyOscVideo is free software: you can redistribute it and/or modify          *
#  it under the terms of the GNU General Public License as published by        *
#  the Free Software Foundation, either version 3 of the License, or           *
#  (at your option) any later version.                                         *
#                                                                              *
#  pyOscVideo is distributed in the hope that it will be useful,               *
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              *
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               *
#  GNU General Public License for more details.                                *
#                                                                              *
#  You should have received a copy of the GNU General Public License           *
#  along with pyOscVideo.  If not, see <https://www.gnu.org/licenses/>.        *
# ******************************************************************************
import time
from multiprocessing import Process, Queue
import cv2

# pylint: disable=C0103
# pylint: disable=global-statement
time_then = 0
counter = 0
frame_rate = 30
CAMERA = 2
#CODEC = 1196444237.0 # MJPG
CODEC = 844715353.0 # YUY2

def set_camera_codec(cap):
    '''Set the camera codec'''
    # NOTE: Even if it returns true this doesn't ensure that the property value
    # has been accepted by the capture device. See note in VideoCapture.get()
    success = cap.set(cv2.CAP_PROP_FOURCC, CODEC)
    return success

def check_camera_codec(cap):
    '''Print the camera codec'''
    codec = cap.get(cv2.CAP_PROP_FOURCC)
    print('codec: ' + str(codec))

def stream_loop(cap):
    '''Show the camera stream'''
    q = Queue()
    writer = Process(target=write, args=(q,))
    writer.start()
    i=0
    while True:
        # Capture frame-by-frame
        global time_then, counter, frame_rate

        ret, frame = cap.read()
        counter += 1

        #if time_elapsed > 1./frame_rate:
        # Display the resulting frame
        q.put(frame)
        if ret:
            time_elapsed = time.time() - time_then
            cv2.imshow('frame', frame)
            if i % 30 == 0:
                print('Fps: %.2f' % (1./time_elapsed))
            i+=1
            time_then = time.time()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Cannot grab frame")
            
import random

def write(queue):
    fps = 0
    last = 0
    wqueue = Queue()
    p = Process(target=dowrite, args=(wqueue,))
    p.start()
    last = time.time()
    last_frame = queue.get()
    while True:
        now = time.time()
        if (now-last) < 1/25.0:
            time.sleep(1/25.0 - (now-last))
        try:
            frame = queue.get_nowait()
        except:
            frame = last_frame
        wqueue.put(frame)
        last_frame = frame
        while not queue.empty():
            queue.get_nowait()
        last = now

def dowrite(queue):
    writer = cv2.VideoWriter(f"/tmp/v{random.random()}.avi", cv2.VideoWriter_fourcc('M','J','P','G'), 25, (640, 480))
    while True:
        frame = queue.get()
        writer.write(frame)

def print_size(cap):
    '''Print the capture size'''
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = (width, height)
    print("Camera size: " + str(size))

def set_frame_rate(cap):
    '''Set the frame rate'''
    cap.set(cv2.CAP_PROP_FPS, frame_rate)

def set_size(cap, width, height):
    '''Set the capture size'''
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

def main():
    '''Run the program'''
    global time_then, counter, frame_rate
    counter = 0

    time_then = time.time()
    cap = cv2.VideoCapture(CAMERA)
    cap2 = cv2.VideoCapture(6)

    while not cap.isOpened() or not cap2.isOpened():
        time.sleep(0.5)
        print('Waiting for camera to open')

    cap.set(cv2.CAP_PROP_BRIGHTNESS, 1)
    cap2.set(cv2.CAP_PROP_BRIGHTNESS, 1)
    success = set_camera_codec(cap)
    success = set_camera_codec(cap2)
    print(success)
    if not success:
        print('Could not set camera codec')

    check_camera_codec(cap)
    check_camera_codec(cap2)

    #print('fourcc:', decode_fourcc(codec))
    print_size(cap)
    print_size(cap2)


    set_frame_rate(cap)
    set_frame_rate(cap2)

    set_size(cap, 640, 480)
    set_size(cap2, 640, 480)
    #set_frame_rate()

    print_size(cap)
    print_size(cap2)

    time.sleep(0.5)
    print("frame rate: " + str(cap.get(cv2.CAP_PROP_FPS)))

    p1 = Process(target=stream_loop, args=(cap,))
    p2 = Process(target=stream_loop, args=(cap2,))

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    # When everything done, release the capture
    cap.release()
    cap2.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

