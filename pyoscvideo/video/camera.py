# *****************************************************************************
#  Copyright (c) 2020. Pascal Staudt, Bruno Gola                              *
#                                                                             *
#  This file is part of pyOscVideo.                                           *
#                                                                             *
#  pyOscVideo is free software: you can redistribute it and/or modify         *
#  it under the terms of the GNU General Public License as published by       *
#  the Free Software Foundation, either version 3 of the License, or          *
#  (at your option) later version.                                        *
#                                                                             *
#  pyOscVideo is distributed in the hope that it will be useful,              *
#  but WITHOUT ANY WARRANTY; without even the implied warranty of             *
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              *
#  GNU General Public License for more details.                               *
#                                                                             *
#  You should have received a copy of the GNU General Public License          *
#  along with pyOscVideo.  If not, see <https://www.gnu.org/licenses/>.       *
# *****************************************************************************

import logging
import queue
import time
import numpy as np

from typing import Callable, Optional, Dict, Any, Tuple

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QImage
from cv2.cv2 import VideoWriter_fourcc

from pyoscvideo.video.camera_reader import CameraReader
from pyoscvideo.video.video_writer import VideoWriter


class Camera(QObject):
    """
    Abstracts a video streamer from a camera.
    """
    device_id: int
    frame_counter: int
    is_capturing: bool
    is_recording: bool
    name: str
    recording_fps: int
    recording_info: Optional[Dict['str', Any]]

    def __init__(self, device_id: int, name: str,
                 resolution: Optional[Dict[str, int]] = None,
                 codec: str = "MJPG", recording_fps: int = 25,
                 recording_resolution: Optional[Dict[str, int]] = None):
        """
        Init the camera object, prepare the supporting camera reader,
        video writer and fps update threads.
        """
        super().__init__()
        self._logger = logging.getLogger(__name__ + f".Camera[{name}]")
        self._logger.info("Initializing")

        self._codec = codec
        fourcc = VideoWriter_fourcc(*codec)
        self._options = {
            "CAP_PROP_FOURCC": fourcc,
            }

        self._resolution = None
        if resolution:
            self._resolution = (resolution["width"], resolution["height"])
            self._options.update({
                "CAP_PROP_FRAME_WIDTH": resolution["width"],
                "CAP_PROP_FRAME_HEIGHT": resolution["height"],
            })

        self._recording_resolution: Optional[Tuple[int, int]] = None
        if recording_resolution:
            self._recording_resolution = (
                    recording_resolution["width"],
                    recording_resolution["height"]
                    )
        else:
            if resolution:
                self._recording_resolution = (
                        resolution["width"],
                        resolution["height"]
                        )

        self.device_id = device_id
        self.frame_counter = 0

        self.name = name

        self.is_capturing = False
        self.is_recording = False
        self.recording_fps = recording_fps
        self.recording_info = {}

        self._image_update_thread = None
        self._init_reader_and_writer()
        self._fps_update_thread: Optional[UpdateFps] = None

    def _init_reader(self):
        """
        Initializes the CameraReader, which is responsible for managing
        a thread for reading frames from the camera.
        """
        self._camera_reader = CameraReader(self._read_queue, self._options)

    def _init_writer(self):
        """
        Initializes the VideoWriter, which is responsible for managing
        the thread for writing frames to a file keeping constant frame rate.
        """
        if self._recording_resolution is None:
            self._recording_resolution = self._camera_reader.frame_size

        self._writer = VideoWriter(self._write_queue,
                                   self._codec,
                                   self.recording_fps,
                                   self._recording_resolution)

    def check_frame_size(self) -> Tuple[bool, Tuple[int, int]]:
        """
        Checks if the captured frame size is the same as the configured one.

        Raises ValueError if called before starting to capture.
        """
        if not self.is_capturing:
            raise ValueError(
                    "Can't check frame size before starting to capture")
        return (self._camera_reader.frame_size == self._resolution,
                self._camera_reader.frame_size)

    @property
    def fail_msg(self):
        if self._camera_reader:
            return self._camera_reader.fail_msg
        return ""

    def _failed_capturing(self):
        """
        Called when capture failed for some reason. Updates the current status
        and tries to gather information on the failure.
        """
        self.is_recording = False
        self.is_capturing = False
        self._logger.error(f"Could not start capturing: {self.fail_msg}")

    def start_capturing(self) -> bool:
        """
        Start capturing frames from the defined source.

        Creates CameraReader Object and sets the source and the state
        """
        self._logger.info("Start capturing")

        if self.is_capturing:
            return True

        if (self._camera_reader.set_camera(self.device_id) and
                self._camera_reader.ready):
            self._logger.info("Capturing started")
            self._start_image_update_thread()
            self._start_fps_update_thread()
            self.is_capturing = True
            return True

        self._failed_capturing()
        return False

    def stop_capturing(self):
        """
        Stops capturing, cleans self and reinit camera reader and video writer.
        """
        self._logger.info("Stopping capture")

        if self.is_recording:
            self.stop_recording()

        self.cleanup()

        self._image_update_thread = None
        self.is_capturing = False
        self._init_reader_and_writer()

    def _init_reader_and_writer(self):
        """
        Initializes both camera reader and video writer.
        """
        self._camera_reader: Optional[CameraReader] = None
        self._read_queue: queue.LifoQueue = queue.LifoQueue()
        self._init_reader()

        self._writer = None
        self._write_queue: queue.LifoQueue = queue.LifoQueue()
        self._init_writer()

    def prepare_recording(self, filename: str) -> bool:
        """
        Prepare the recording.

        If not capturing yet, starts the capturing, and tries to create a file
        with the set file extension.
        """
        self._logger.info("Preparing recording: %s", filename)

        if not self.is_capturing:
            if not self.start_capturing():
                return False

        if not self._writer.prepare_writing(filename):
            return False

        self._camera_reader.add_queue(self._write_queue)

        return True

    def _start_image_update_thread(self):
        """
        Start the capturing of frames.

        Spawns the image update thread.
        """
        if self._image_update_thread:
            self._image_update_thread.stop()

        self._image_update_thread = UpdateImage(self._read_queue)
        # TODO:
        # There is an strage bug here, if we use the self.on_new_frame
        # as callback it won't be called, but with a lambda it works
        self._image_update_thread.new_frame.connect(
                lambda: self.on_new_frame())
        self._image_update_thread.start()

    def add_update_fps_label_cb(self, callback: Callable[[float], None]):
        """
        Sets a function to be called with the current capture frame rate.
        """
        assert self._fps_update_thread is not None
        self._fps_update_thread.updateFpsLabel.connect(callback)

    def remove_update_fps_label_cb(self, callback: Callable[[float], None]):
        """
        Removes a previously set function to be called with the current capture
        frame rate.
        """
        assert self._fps_update_thread is not None
        self._fps_update_thread.updateFpsLabel.disconnect(callback)

    def add_change_pixmap_cb(self, callback: Callable[[np.array], None]):
        """
        Sets a function to be called with the current captured frame as
        argument.
        """
        if self._image_update_thread is None:
            self._logger.error("Image update thread is not running")
            return
        self._image_update_thread.change_pixmap.connect(callback)

    def remove_change_pixmap_cb(self, callback: Callable[[np.array], None]):
        """
        Remove a previously set function to be called with the current captured
        frame as argument.
        """
        if self._image_update_thread is None:
            self._logger.error("Image update thread is not running")
            return
        self._image_update_thread.change_pixmap.disconnect(callback)

    def _start_fps_update_thread(self):
        """Spawn the fps update thread."""
        self._fps_update_thread = UpdateFps(self)
        self._fps_update_thread.start()

    def start_recording(self):
        """Start the recording.
        """
        if self._camera_reader.ready and self._writer.ready:
            self.recording_info = {}
            self._writer.start_writing()
            self.is_recording = True
            self._logger.info("Started recording")
            return True

        self.is_recording = False
        self._logger.error(
            "Could not start recording, camera reader or writer not ready")
        return False

    def stop_recording(self):
        """Stop the recording and print out statistics.

        TODO: add return values
        """
        if self.is_recording:
            frames_written, recording_time, frames_repeated = (
                    self._writer.stop_writing()
                )
            self._camera_reader.remove_queue(self._write_queue)
            self.is_recording = False
            self._logger.info("Stopped recording")
            self._logger.info(
                f"Recording Time: {recording_time:.1f}s")
            self._logger.info(f"{int(frames_written)} frames written")
            if recording_time > 0:
                avg = frames_written / recording_time
                self._logger.info(f"Average frame rate: {avg:.2f}")
            self.recording_info["time"] = recording_time
            self.recording_info["fps"] = avg
            self.recording_info["resolution"] = self._recording_resolution
            self.recording_info["frames"] = frames_written
            self.recording_info["frames_repeated"] = frames_repeated
            # Re-init the writer
            # TODO: review this because it doesn't seem correct to re-init
            # it here
            self._writer = None
            self._init_writer()
        else:
            self._logger.warning("Not recording")

    def on_new_frame(self):
        """
        Called when a new frame is captured by the camera reader.
        """
        self.frame_counter += 1

    def cleanup(self):
        """
        Perform necessary action to guarantee a clean exit of the app.
        """
        self._camera_reader.stop_buffering()
        self._camera_reader.release()

        self._writer.release()

        self._fps_update_thread.stop()
        self._fps_update_thread.wait()

        if self._image_update_thread:
            self._image_update_thread.stop()
            self._image_update_thread.wait()


class UpdateFps(QThread):
    """Calculate current framerate every second and update the Fps label."""

    updateFpsLabel = pyqtSignal(float)

    def __init__(self, camera: Camera):
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".UpdateFps")
        self._time_last_update = time.time()
        self._camera = camera
        self._quit = False

    def stop(self):
        self._quit = True

    def run(self):
        """Run the Thread worker."""
        self._logger.info("Started fps label update thread")
        while not self._quit:
            time_now = time.time()
            time_passed = time_now - self._time_last_update
            frame_rate = float(self._camera.frame_counter / time_passed)
            self._camera.frame_counter = 0
            self.updateFpsLabel.emit(frame_rate)
            self._time_last_update = time.time()
            time.sleep(1)


class UpdateImage(QThread):
    """ Thread for reading frames from the source and updating the image
    """
    new_frame = pyqtSignal()
    change_pixmap = pyqtSignal(QImage)

    def __init__(self, frame_queue):
        """Init the UpdateImage Thread."""
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".UpdateImage")
        self._queue = frame_queue
        self._quit = False

    def stop(self):
        self._quit = True

    def run(self):
        """Run the worker."""
        self._logger.info("Started image update thread")

        forward_frames = 0
        while not self._quit:
            try:
                frame = self._queue.get(timeout=0.2)
            except queue.Empty:
                self._logger.warning("Timed out waiting for a frame")
                continue
            self._logger.debug("emit image")
            image = self.cv2qt(frame)
            self.change_pixmap.emit(image)
            self.new_frame.emit()
            while not self._queue.empty():
                # discard other frames if any
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    continue

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
