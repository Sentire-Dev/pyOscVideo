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

from typing import List

from pyoscvideo.video.camera import Camera
from pyoscvideo.models import MainModel


def _generate_filename():
    time_str = time.strftime("%Y%m%d_%H%M%S")
    filename = "OSCVideo_Recording_" + time_str
    return filename


class MainController:
    """
    The main controller is responsible for keeping track of the overall state
    of the software and dealing with multiple cameras.

    Most methods will call a similar method for each of the cameras in use,
    for example when start to capture or record.
    """
    # TODO: better name than main controller

    def __init__(self, cameras: List[Camera]):
        """
        Init the main controller.
        """
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".MainController")
        self._logger.info("Initializing")
        self._model = MainModel()

        self._cameras = cameras

    def start_capturing(self) -> bool:
        """
        Starts capturing for each of the tracked cameras.
        """
        for camera in self._cameras:
            if not camera.start_capturing():
                return False
        return True

    def prepare_recording(self, filename) -> bool:
        """
        Prepares the recording.

        If not capturing yet, starts the capturing, and tries to create a file
        with the set file extension.
        """
        if not self._model.is_recording:
            for i, camera in enumerate(self._cameras):
                if not camera.prepare_recording(f"{filename}_camera{i}.avi"):
                    return False
        else:
            self._logger.warning("Already recording")
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

    def start_recording(self) -> bool:
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
        for camera in self._cameras:
            camera.cleanup()
