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

import logging
import queue
import time
import numpy as np

from typing import Dict, Any, Type
from PyQt5.QtCore import QObject, pyqtSignal

from pyoscvideo.video.camera import Camera
from pyoscvideo.video.camera_selector import CameraSelector, BaseCameraSelector


def _generate_filename():
    time_str = time.strftime("%Y%m%d_%H%M%S")
    filename = "OSCVideo_Recording_" + time_str
    return filename


class VideoManager(QObject):
    """
    The main controller is responsible for keeping track of the overall state
    of the software and dealing with multiple cameras.

    Most methods will pass on the call for each camera in use.
    """
    # TODO: better name than main controller
    is_recording_changed = pyqtSignal(bool)
    status_msg_changed = pyqtSignal(str)

    def __init__(self, camera_selector: Type[BaseCameraSelector]):
        """
        Init the main controller.
        """
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".VideoManager")
        self._logger.info("Initializing")

        self._cameras: Dict[Camera, int] = {}
        self._is_recording = False
        self._status_msg = ''

        self.camera_selector = camera_selector

    @property
    def is_recording(self):
        return self._is_recording

    @is_recording.setter
    def is_recording(self, value: bool):
        self.is_recording_changed.emit(value)
        self._is_recording = value

    @property
    def status_msg(self):
        return self._is_recording

    @status_msg.setter
    def status_msg(self, value: str):
        self.status_msg_changed.emit(value)
        self._status_msg = value

    def use_camera(self, camera: Camera) -> bool:
        if camera.start_capturing():
            camera_count = self._cameras.get(camera, 0)
            self._cameras[camera] = camera_count + 1
            self._logger.info(f"Using camera {camera.name}.")
            return True
        return False

    def unuse_camera(self, camera: Camera):
        camera_count = self._cameras.get(camera, 0)
        self._logger.info(f"Unuse camera {camera.name}.")

        # camera not in use anymore
        if camera_count <= 1:
            self._logger.info(
                f"Camera {camera.name} is not used anymore, stop capturing.")
            camera.stop_capturing()
            del self._cameras[camera]
            return

        self._cameras[camera] = camera_count - 1

    @property
    def cameras(self):
        return self._cameras

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
        if not self.is_recording:
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
        if not self.is_recording:
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
        if not self.is_recording:
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
        self.is_recording = True
        return True

    def stop_recording(self):
        """Stop the recording and print out statistics.

        TODO: add return values
        """
        for camera in self._cameras:
            camera.stop_recording()
        self.is_recording = False

    def cleanup(self):
        """Perform necessary action to guarantee a clean exit of the app."""
        if self.is_recording:
            self.stop_recording()

        for camera in self._cameras:
            camera.cleanup()
