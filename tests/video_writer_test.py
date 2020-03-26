"""
    TODO:
        * add file description
        * update implementation
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

import datetime
import json
import logging.config
import os
import time

import cv2

from pyoscvideo.controllers.video_writer import VideoWriter


#from vidgear.gears import CamGear


def setup_logging(
    default_path='./pyoscvideo/logging/logging_settings.json',
    default_level=logging.INFO,
    ):
    """Setup logging configuration

    """
    path = default_path
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        print('Could not find: ' + str(path))


def capPropId(cv_property):
    """
    Retrieves the OpenCV property Integer(Actual) value. 
    """
    integer_value = 0 
    try:
        integer_value = getattr(cv2, cv_property)
    except AttributeError:
        print('{} is not a valid OpenCV property!'.format(cv_property))
        return None
    return integer_value

# setup logging
setup_logging()

# open camera stream
fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')     

options = {"CAP_PROP_FOURCC" : fourcc, 'CAP_PROP_FRAME_WIDTH' : 1280, 'CAP_PROP_FRAME_HEIGHT' : 720}
#stream = CamGear(source=0, logging=True, **options).start() # To open video stream on first index(i.e. 0) device

stream = cv2.VideoCapture(0)

options = {k.strip(): v for k, v in options.items()}
for key, value in options.items():
    stream.set(capPropId(key), value)

fps = 30

# init writer object
foldername =  'recordings'
filename = foldername + '/' + str(datetime.datetime.now()) + '.avi'
FOURCC = "MJPG"

time.sleep(0.5)

writer = VideoWriter(stream, filename, FOURCC, fps)
writer.start_buffering()

time.sleep(0.5)
writer.start_writing()
time.sleep(10)
writer.stop_writing()
frames_written, recording_time = writer.stop_writing()
frames_read = writer.stop_buffering()

# writer.release()
# print("Recording Time: " +  str(recording_time) + "s")
print(str(frames_read) + " frames read")
print(str(frames_written) + " frames written")
if recording_time > 0:
    print("Average frame rate: " + str(frames_written/recording_time) + "fps")
else:
    print("Nothing Recorded")

#time.sleep(3)


