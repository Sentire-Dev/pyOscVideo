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

import cv2
# import libraries
from vidgear.gears import CamGear

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