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

import cv2
from vidgear.gears import CamGear

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