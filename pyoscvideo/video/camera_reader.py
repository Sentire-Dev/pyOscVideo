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
import numpy as np
import cv2

from typing import Any, Dict, List, Tuple, Optional

from PyQt5.QtCore import QThread
from cv2.cv2 import (
    CAP_PROP_FRAME_HEIGHT,
    CAP_PROP_FPS,
    CAP_PROP_FRAME_WIDTH,
    VideoCapture)

from pyoscvideo.helpers.helpers import get_cv_cap_property_id


class CameraReader:
    """
    Buffered reading from a Camera using VideoCapture and pushing frames
    to queue(s) to be consumed.

    The OpenCV caputre can be configured using the `options` argument, see
    set_camera_options().
    """
    stream: Optional[VideoCapture]
    fail_msg: str

    def __init__(self, frame_queue: queue.LifoQueue, options: Dict[str, Any]):
        """Init the CameraReader."""
        self._logger = logging.getLogger(__name__ + ".CameraReader")
        self._logger.info("Initializing")
        self._options = options
        self._queues = [frame_queue]
        self._num_clients = 0
        self._read_thread = None
        self._reading_finished = True
        self._buffering = False
        self._ready = False
        self.stream = None
        self.fail_msg = ""
        self.frame_size: Optional[Tuple[int, int]] = None

    @property
    def ready(self) -> bool:
        """Check if reader is ready."""
        if (
                self.stream is not None and
                self.stream.isOpened()):
            return True
        return False

    @property
    def width(self) -> int:
        """Get the width."""
        if self.ready:
            assert self.stream is not None
            return int(self.stream.get(CAP_PROP_FRAME_WIDTH))
        self._logger.warning("Camera is not ready")
        return 0

    @width.setter
    def width(self, value):
        """Set the width."""
        # TODO: Implement
        self._logger.warning("setting size not implemented")
        raise NotImplementedError

    @property
    def height(self) -> int:
        """Get the height."""
        if self.ready:
            assert self.stream is not None
            return int(self.stream.get(CAP_PROP_FRAME_HEIGHT))
        self._logger.warning("Camera is not ready")
        return 0

    @height.setter
    def height(self, value):
        """Set the height."""
        # TODO: Implement
        self._logger.warning("setting size not implemented")
        raise NotImplementedError

    @property
    def size(self) -> Tuple[int, int]:
        """Get the size."""
        return (self.width, self.height)

    @size.setter
    def size(self, value):
        """Set the size."""
        # TODO: Implement
        self._logger.warning("setting size not implemented")
        raise NotImplementedError

    @property
    def frame_rate(self) -> float:
        """Get the frame rate."""
        if self.ready:
            assert self.stream is not None
            frame_rate = self.stream.get(CAP_PROP_FPS)
            return frame_rate
        self._logger.warning("Camera is not ready")
        return 0.0

    def set_camera(self, device_id: int) -> bool:
        """
        Set the camera to the given ID.
        """
        self._logger.info("Set camera device: %s", device_id)
        if self._buffering:
            self.stop_buffering()
        if self.ready:
            self.release()
        if self.open_camera(device_id):
            return True
        return False

    def open_camera(self, device_id: int) -> bool:
        """
        Open the camera with the given ID.
        """
        self.fail_msg = ""
        try:
            self.stream = VideoCapture(device_id)
        except RuntimeError as err:
            print(f"Could not open Camera with ID {device_id}: {err}")
            self.fail_msg = str(err)
            return False

        self.set_camera_options(self._options)

        # check size
        success, frame = self.stream.read()
        if success:
            self.frame_size = (frame.shape[1], frame.shape[0])
            config_size = (
                    self._options.get("CAP_PROP_FRAME_WIDTH", self.size[0]),
                    self._options.get("CAP_PROP_FRAME_HEIGHT", self.size[1]))

            self._logger.info("Camera Stream Ready")
            if self.frame_size != config_size:
                self._logger.warning(
                        f"Capture size is different from the configured one: "
                        f"{config_size} != {self.frame_size}")
            else:
                self._logger.info(f"Capture Size: {self.frame_size}")
            self._logger.info(f"Camera Fps: {self.frame_rate}")
            self.start_buffering()
            return True

        self._logger.warning("Camera not ready, can't open.")
        return False

    def set_camera_options(self, options: Dict[str, Any]) -> None:
        """Set the camera options.

        Important (see https://github.com/abhiTronix/vidgear/wiki/camgear):
            Remember, not all of the OpenCV parameters are supported by all
            cameras. Each camera type, from android cameras to USB cameras to
            professional ones offers a different interface to modify its
            parameters. Therefore there are many branches in OpenCV code to
            support as many of them, but of course, not all possible devices
            are covered and therefore works.

            Therefore, To check parameter values supported by your webcam, you
            can hook your camera to your Linux machine and use command
            v4l2-ctl -d 0 --list-formats-ext (where 0 is the index of the given
            camera) to list the supported video parameters and their values Or
            directly refer to the device corresponding datasheet, if available.

        Arguments:
            options {dict} -- Dictionary of opencv capture properties

        Example:
            fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
            set_camera_options({"CAP_PROP_FOURCC" : fourcc,
                                "CAP_PROP_FRAME_WIDTH'": 1280,
                                "CAP_PROP_FRAME_HEIGHT" : 720})

        TODO: check if valid options, check if setting was successful
        """
        if not self.ready:
            self._logger.warning("Camera not ready, can't set options.")
            return

        assert self.stream is not None

        self._logger.info("Setting camera options")
        options = {k.strip(): v for k, v in options.items()}
        for key, value in options.items():
            success = self.stream.set(get_cv_cap_property_id(key), value)
            self._logger.info("[%s, %s]: success %s", key, value, success)

    def start_buffering(self):
        """
        Start the buffering of frames.

        Spawns a ReadThread Instance
        """
        self._logger.info("Start buffering")
        self._reading_finished = False
        self._buffering = True
        self._read_thread = ReadThread(self._queues, self.stream)
        self._read_thread.start()

    def stop_buffering(self) -> int:
        """
        Stop the buffering of frames.

        Stops the ReadThread and waits for it to finish, returning the
        number of frames read.
        """
        self._logger.info("Stop buffering")
        self._buffering = False

        if self._read_thread:
            self._read_thread.stop = True
            self._read_thread.quit()
            self._read_thread.wait()
            self._logger.info(self._read_thread.isRunning())

            return self._read_thread.frames_read
        return 0

    def release(self):
        """Release the camera."""
        if self.stream:
            self.stream.release()

    def add_queue(self, frame_queue: queue.LifoQueue) -> None:
        """Add a queue to the camera reader processed queues.

        When not needed anymore, the queue should be removed. See
        remove_queue(frame_queue)
        """
        self._queues.append(frame_queue)

    def remove_queue(self, frame_queue: queue.LifoQueue) -> None:
        """
        Remove the given frame_queue from the list of processed queues.
        """
        self._queues.remove(frame_queue)


class ReadThread(QThread):
    """
    Thread for reading frames from the stream.

    Will consume frames from a VideoCapture stream and push it to
    multiple queues to be consumed by other threads.
    """

    stop: bool

    def __init__(self, queues: List[queue.LifoQueue], stream: VideoCapture):
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".ReadThread")
        self._logger.info('Initializing ReadThread')
        self._queues = queues
        self._stream = stream
        self._frames_read = 0
        self.stop = False

    @property
    def frames_read(self) -> int:
        """
        Get the number of read frames.
        """
        return self._frames_read

    def run(self):
        """Start the worker function of the ReadThread."""
        self._frames_read = 0
        self._logger.info('Started reading')
        while not self.stop:
            # self._logger.debug("loop")
            # success = True
            success, frame = self._stream.read()
            if success:
                self._frames_read += 1
                # self._logger.debug("read frame %s", self._frames_read)
                self._write_frame_to_queues(frame)
            else:
                self._logger.debug("could not read frame")
            # time.sleep(1 / self.fps)
            # continue
        self._logger.info('Finished reading')

    def _write_frame_to_queues(self, frame: np.array):
        for i_queue in self._queues:
            i_queue.put(frame)
