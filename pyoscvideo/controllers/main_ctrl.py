# *****************************************************************************
#  Copyright (c) 2020. Pascal Staudt, Bruno Gola                              *
#                                                                             *
#  This file is part of pyOscVideo.                                           *
#                                                                             *
#  pyOscVideo is free software: you can redistribute it and/or modify         *
#  it under the terms of the GNU General Public License as published by       *
#  the Free Software Foundation, either version 3 of the License, or          *
#  (at your option) any later version.                                        *
#                                                                             *
#  pyOscVideo is distributed in the hope that it will be useful,              *
#  but WITHOUT ANY WARRANTY; without even the implied warranty of             *
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              *
#  GNU General Public License for more details.                               *
#                                                                             *
#  You should have received a copy of the GNU General Public License          *
#  along with pyOscVideo.  If not, see <https://www.gnu.org/licenses/>.       *
# *****************************************************************************

# pylint: disable=trailing-whitespace
"""Source Code for the MainController Class of the pyoscvideo module.

TODO: add proper file description
"""

import logging
import queue
import time
import numpy as np

from typing import Callable, Optional

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QImage
from cv2.cv2 import VideoWriter_fourcc

from pyoscvideo.video.camera_reader import CameraReader
from pyoscvideo.video.camera_selector import CameraSelector
from pyoscvideo.video.video_writer import VideoWriter
from pyoscvideo.helpers import helpers
from pyoscvideo.models import MainModel

# TODO: Global variables should not be defined here
#       instead use Settings Class
# FOURCC = -1 # Should output available codecs, not working at the moment

# The default codec, works on arch and mac together with .avi extensions
FOURCC = "MJPG"
# FOURCC = "xvid" # The default codec
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080
PLAY_FILENAME = "output"
LISTEN_PORT = 1234
FPS = 25
TARGET_PORT = 57120
TARGET_HOSTNAME = "localhost"
WINDOW_NAME = "OSCVideo"
CAMERAS = 1

def _generate_filename():
    time_str = time.strftime("%Y%m%d_%H%M%S")
    filename = "OSCVideo_Recording_" + time_str
    return filename


            
class MainController(QObject):
    """
    The main controller object.
    """
    # TODO: better name than main controller

    def __init__(self, cameras):
        """
        Init the main controller.
        """
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".CameraController")
        self._logger.info("Initializing")
        self._model = MainModel()

        self._cameras = cameras

    def start_capturing(self):
        for camera in self._cameras:
            if not camera.start_capturing():
                return False
        return True

    def prepare_recording(self, filename):
        """Prepare the recording.

        If not capturing yet, starts the capturing, and tries to create a file
        with the set file extension.

        TODO: provide return value indicating if preparation was successful
        """
        if not self._model.is_recording:
            for i, camera in enumerate(self._cameras):
                if not camera.prepare_recording(f"{filename}_camera{i}.avi"):
                    return False
        else:
            self.logger.warning("Already recording")
        return True

    def toggle_recording(self):
        """Toggle the Recording.

        If not recording make a new recording with time stamped filename.
        Otherwise stop the current recording.
        """
        self._logger.info("Toggle Recording")
        if not self._model.is_recording:
            filename = _generate_filename()
            self.new_recording(filename)
        else:
            self.stop_recording()

    def new_recording(self, filename):
        """Start a new recording.

        Stops the current recording, prepares a new one and starts it.

        Arguments:
            filename {String} -- the filename of the recording

        Note:
            Should only be called if instantaneous recording is not needed
            since it takes some time to prepare the recording.

        See Also:
            prepare_recording()
        """
        if not self._model.is_recording:
            if self.prepare_recording(filename):
                self.start_recording()
            else:
                self._logger.warning(
                        "Could not start Recording. Check filename")
        else:
            self.stop_recording()
            self.new_recording(filename)
 
    def start_recording(self):
        """Stop the recording and print out statistics.

        TODO: add return values
        """
        for camera in self._cameras:
            if not camera.start_recording():
                return False
        self._model.is_recording = True
        return True

    def stop_recording(self):
        """Stop the recording and print out statistics.

        TODO: add return values
        """
        for camera in self._cameras:
            camera.stop_recording()
        self._model.is_recording = False

    def cleanup(self):
        """Perform necessary action to guarantee a clean exit of the app."""


class UpdateFps(QThread):
    """Calculate current framerate every second and update the Fps label."""

    updateFpsLabel = pyqtSignal(float)

    def __init__(self, model):
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".UpdateFps")
        self._model = model
        self._time_last_update = time.time()
        self._update_interval = 1

    def run(self):
        """Run the Thread worker."""
        self._logger.info("Started fps label update thread")
        while True:
            time_now = time.time()
            time_passed = time_now - self._time_last_update
            frame_rate = float(self._model.frame_counter / time_passed)
            self._model.frame_counter = 0
            self.updateFpsLabel.emit(frame_rate)
            self._time_last_update = time.time()
            time.sleep(1)


class UpdateImage(QThread):
    """ Thread for reading frames from the source and updating the image
    """
    new_frame = pyqtSignal()
    change_pixmap = pyqtSignal(QImage)

    def __init__(self, frame_queue, frame_rate):
        """Init the UpdateImage Thread."""
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".UpdateImage")
        self._queue = frame_queue

        if frame_rate == 0:
            self._logger.error("Frame rate cannot be 0")
            raise RuntimeError
        self._frame_duration = 1 / frame_rate
        self._time_last_update = time.time()

    def run(self):
        """Run the worker."""
        self._logger.info("Started image update thread")

        forward_frames = 0
        while True:
            while not self._queue.empty():
                try:
                    frame = self._queue.get_nowait()
                    self._logger.debug("emit image")
                    image = self.cv2qt(frame)
                    self.change_pixmap.emit(image)
                    self.new_frame.emit()
                    self._time_last_update = time.time()
                except queue.Empty:
                    # exception raised sometimes anyway
                    # check again:
                    if self._queue.empty():
                        self._logger.debug("queue is empty")
                        self._logger.debug("fast forward frame")
                        forward_frames += 1
            delta_time = time.time() - self._time_last_update
            self._logger.debug("Queue is empty")
            if delta_time < self._frame_duration:
                sleep = self._frame_duration - delta_time
                self._logger.debug("Waiting %s seconds", sleep)
                time.sleep(sleep)

    @staticmethod
    def cv2qt(frame):
        """Convert an image frame from cv to qt format.

        Arguments:
            frame {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        qt_format = QImage.Format_Indexed8
        if len(frame.shape) == 3:
            if frame.shape[2] == 4:
                qt_format = QImage.Format_RGBA8888
            else:
                qt_format = QImage.Format_RGB888

        cv_image = QImage(frame, frame.shape[1], frame.shape[0],
                          frame.strides[0], qt_format)
        cv_image = cv_image.rgbSwapped()
        return cv_image
