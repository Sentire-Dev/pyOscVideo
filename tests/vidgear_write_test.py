from vidgear.gears import CamGear
from vidgear.gears import WriteGear
import cv2

# Open live webcam video stream on first index(i.e. 0) device
fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')        
options = {"CAP_PROP_FOURCC" : fourcc, 'THREADED_QUEUE_MODE':True, 'CAP_PROP_FRAME_WIDTH' : 1280, 'CAP_PROP_FRAME_HEIGHT' : 720}
stream = CamGear(source=0, logging=True, **options).start() # To open video stream on first index(i.e. 0) device

#output_params = {"-vcodec":"libx264", "-crf": 0, "-preset": "fast", "tune": "zerolatency"} 
output_params = {"-fourcc":"MJPG", "-fps": 30} 
writer = WriteGear(output_filename='Output.avi',
                   compression_mode=False, output_params=output_params)  # Define writer

#writer = WriteGear(output_filename='Output.mp4') #Define writer 

# infinite loop
while True:

    frame = stream.read()
    # read frames

    # check if frame is None
    if frame is None:
        # if True break the infinite loop
        break

    # do something with frame here

    # write frame to writer
    writer.write(frame)

    # Show output window
    cv2.imshow("Output Frame", frame)

    key = cv2.waitKey(1) & 0xFF
    # check for 'q' key-press
    if key == ord("q"):
        # if 'q' key-pressed break out
        break

cv2.destroyAllWindows()
# close output window

stream.stop()
# safely close video stream
writer.close()
# safely close writer
