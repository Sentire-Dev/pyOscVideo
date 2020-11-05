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
import os

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
    is_recording_changed = pyqtSignal(bool)
    is_capturing_changed = pyqtSignal(bool)
    status_msg_changed = pyqtSignal(str)

    def __init__(self, camera_options: Dict[str, Any]):
        """
        Init the main controller.
        """
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".VideoManager")
        self._logger.info("Initializing")

        self._cameras: Dict[Camera, int] = {}
        self._is_recording = False
        self._is_capturing = False
        self._status_msg = ''
        self._recording_dir = None

        self.camera_selector = CameraSelector(camera_options)

    @property
    def is_capturing(self):
        return self._is_capturing

    @is_capturing.setter
    def is_capturing(self, value: bool):
        self.is_capturing_changed.emit(value)
        self._is_capturing = value

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
        self._logger.info(f"Status changed: {value}")

    def use_camera(self, camera: Camera) -> bool:
        """
        Registers a camera as in use, starts capturing if it's not capturing
        yet.

        Can hold multiple instances of the same camera.
        """
        if self.is_recording:
            self._logger.warning("Can't change cameras while recording")
            return False

        if camera.start_capturing():
            camera_count = self._cameras.get(camera, 0)
            self._cameras[camera] = camera_count + 1
            self._logger.info(f"Using camera {camera.name}.")
            success, resolution = camera.check_frame_size()
            if not success:
                self.status_msg = (
                    f"{camera.name} is capturing in the wrong "
                    f"resolution: {resolution}")

            if not self.is_capturing:
                self.is_capturing = True
            return True

        return False

    def unuse_camera(self, camera: Camera):
        """
        Stops using a camera, if camera is not used anymore stops capturing."
        """
        if self.is_recording:
            self._logger.warning("Can't change cameras while recording")
            return False

        camera_count = self._cameras.get(camera, 0)
        self._logger.info(f"Unuse camera {camera.name}.")

        # camera not in use anymore
        if camera_count <= 1:
            self._logger.info(
                f"Camera {camera.name} is not used anymore, stop capturing.")
            camera.stop_capturing()
            del self._cameras[camera]
            if not self._cameras:
                self.is_capturing = False
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
        if not self.is_capturing:
            if not self._cameras:
                self._logger.warning("No camera(s) selected.")
                return False
            self.start_capturing()

        if not self.is_recording:
            self._recording_dir = filename
            if not os.path.exists(filename):
                os.makedirs(filename)
            for i, camera in enumerate(self._cameras):
                if not camera.prepare_recording(f"{filename}/camera_{i}.mov"):
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
        """Starts recording.

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
        self._write_recording_statistics()
        self.is_recording = False

    def _write_recording_statistics(self):
        path = os.path.join(self._recording_dir, "statistics.txt")
        with open(path, "w") as stats_file:
            for camera in self._cameras:
                camera_stats = camera.recording_info
                stats_file.writelines([
                    f"Camera: {camera.name}\n",
                    f"\tAverage FPS: {camera_stats['fps']:.2f}\n",
                    f"\tResolution: {camera_stats['resolution']}\n",
                    f"\tRecording time: {camera_stats['time']:.1f}s\n",
                    f"\tTotal frames: {camera_stats['frames']}\n",
                    f"\tRepeated frames: {camera_stats['frames_repeated']}\n",
                    "\n"])

    def cleanup(self):
        """Perform necessary action to guarantee a clean exit of the app."""
        if self.is_recording:
            self.stop_recording()

        for camera in self._cameras:
            camera.cleanup()
