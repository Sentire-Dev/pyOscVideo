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
# import required libraries
from vidgear.gears import CamGear

options = {"CAP_PROP_FPS ":30, 'THREADED_QUEUE_MODE':True} # define tweak parameters foryour stream.
stream = CamGear(source=2, logging=True, **options).start() # To open video stream on first index(i.e. 0) device
stream2 = CamGear(source=0, logging=True, **options).start()
stream3 = CamGear(source=6, logging=True, **options).start()
stream4 = CamGear(source=10, logging=True, **options).start() 


# define various attributes and start the stream
print(stream.framerate)
# infinite loop
while True:

	frame = stream.read()
	frame2 = stream2.read()
	frame3 = stream3.read()
	frame4 = stream4.read()
	# read frames

	# check if frame is None
	if frame is None:
		#if True break the infinite loop
		break

	# do something with frame here

	cv2.imshow("Output Frame", frame)
	cv2.imshow("Output Frame2", frame2)
	cv2.imshow("Output Frame3", frame3)
	cv2.imshow("Output Frame4", frame4)



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