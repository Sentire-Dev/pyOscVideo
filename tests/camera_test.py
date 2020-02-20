"""Various Camera Tests.

TODO:
    - add Version number
    - add author
    - add license
"""
import time
import cv2
# pylint: disable=C0103
# pylint: disable=global-statement
time_then = 0
counter = 0
frame_rate = 30
cap = None
CAMERA = 0
CODEC = 1196444237.0 # MJPG
#CODEC = 844715353.0 # YUY2

def set_camera_codec():
    '''Set the camera codec'''
    global cap
    # NOTE: Even if it returns true this doesn't ensure that the property value
    # has been accepted by the capture device. See note in VideoCapture.get()
    success = cap.set(cv2.CAP_PROP_FOURCC, CODEC)
    return success

def check_camera_codec():
    '''Print the camera codec'''
    codec = cap.get(cv2.CAP_PROP_FOURCC)
    print('codec: ' + str(codec))

def stream_loop():
    '''Show the camera stream'''
    while True:
        # Capture frame-by-frame
        global time_then, counter, frame_rate

        ret, frame = cap.read()
        counter += 1

        #if time_elapsed > 1./frame_rate:
        # Display the resulting frame
        if ret:
            time_elapsed = time.time() - time_then
            cv2.imshow('frame', frame)
            print('Fps: %.2f' % (1./time_elapsed))
            time_then = time.time()

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Cannot grab frame")
            

def print_size():
    '''Print the capture size'''
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = (width, height)
    print("Camera size: " + str(size))

def set_frame_rate():
    '''Set the frame rate'''
    cap.set(cv2.CAP_PROP_FPS, frame_rate)

def set_size(width, height):
    '''Set the capture size'''
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

def main():
    '''Run the program'''
    global cap, time_then, counter, frame_rate
    counter = 0

    time_then = time.time()
    cap = cv2.VideoCapture(CAMERA)

    while not cap.isOpened():
        time.sleep(0.5)
        print('Waiting for camera to open')

    cap.set(cv2.CAP_PROP_BRIGHTNESS, 1)
    success = set_camera_codec()
    print(success)
    if not success:
        print('Could not set camera codec')

    check_camera_codec()

    #print('fourcc:', decode_fourcc(codec))
    print_size()

    set_frame_rate()

    #set_size(1280, 720)
    #set_frame_rate()

    print_size()

    time.sleep(0.5)
    print("frame rate: " + str(cap.get(cv2.CAP_PROP_FPS)))

    stream_loop()

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

