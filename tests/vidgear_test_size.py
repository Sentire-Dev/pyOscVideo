from vidgear.gears import CamGear
import cv2


#self.options = {"CAP_PROP_FPS ":30, "CAP_PROP_FOURCC" : fourcc, 'THREADED_QUEUE_MODE':True} # define tweak parameters foryour stream.
fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')        
options = {"CAP_PROP_FOURCC" : fourcc, 'THREADED_QUEUE_MODE':True, 'CAP_PROP_FRAME_WIDTH' : 1280, 'CAP_PROP_FRAME_HEIGHT' : 720}
stream = CamGear(source=0, logging=True, **options).start() # To open video stream on first index(i.e. 0) device
width = stream.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
height = stream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
size = [width, height]
fps = stream.framerate
print("size: " + str(size))
print("fps: " + str(fps))

while True:

	frame = stream.read()
	# read frames

	# check if frame is None
	if frame is None:
		#if True break the infinite loop
		break

	# do something with frame here

	cv2.imshow("Output Frame", frame)


	# Show output window

	key = cv2.waitKey(1) & 0xFF
	# check for 'q' key-press
	if key == ord("q"):
		#if 'q' key-pressed exit loop
		break

cv2.destroyAllWindows()
# close output window

stream.stop()
# safely close video stream.