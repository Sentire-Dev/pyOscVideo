# import libraries
from vidgear.gears import CamGear
import cv2
import time

num_frames = 0
# open any valid video stream(for e.g `myvideo.avi` file)
stream = CamGear(0).start() 

time_start = time.time()
# loop
while True:
	# read frames
	frame = stream.read()
	
	# check if frame is None
	if frame is None: break
	
	num_frames += 1
	# do something with frame here


	# Show output window
	cv2.imshow("Output Frame", frame)

	# check for 'q' key-press
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break
		
# close output window
time_end = time.time()
cv2.destroyAllWindows()
# safely close video stream.
stream.stop()
time_passed = time_end - time_start
print("Average fps: %0.2f" % (num_frames/time_passed))