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
import os
import queue
import time
import numpy as np
import cv2

from typing import Optional, Tuple, Union

from PyQt5.QtCore import QThread
from cv2.cv2 import VideoWriter as cvVideoWriter
from cv2.cv2 import VideoWriter_fourcc


class VideoWriter:
    """
    Video writer class for synchronous video writing to file.

    Consumes frames from a queue and will keep a constant FPS, skipping
    or repeating frames if needed.
    """

    def __init__(self, frame_queue: queue.LifoQueue, fourcc: int,
                 frame_rate: int, size: Tuple[int, int]):
        """Init the VideoWriter Object."""
        # pylint: disable=unused-argument
        self._logger = logging.getLogger(__name__ + '.VideoWriter')
        self._logger.info("Initializing")
        self._queue = frame_queue

        # parsing option arguments
        fourcc_id = fourcc
        self._fourcc = VideoWriter_fourcc(*fourcc_id)
        self._fps = int(frame_rate)

        # get the right size from the video stream
        self._size = size
        self._logger.info("Stream size: %s", self._size)
        self._logger.info("Frame rate: %s", self._fps)

        # init writer thread
        self._writer = None
        self._writing = False
        self._write_thread: Optional[WriteThread] = None

        # TODO: check if folder exists
        self._stop = False

    @property
    def size(self) -> Tuple[int, int]:
        return self._size

    @size.setter
    def size(self, value: Tuple[int, int]) -> None:
        if self._writing:
            self._logger.warning("Cannot set size during writing")
        else:
            self._size = value

    @property
    def ready(self) -> bool:
        """Get the status."""
        return self._writer is not None and self._writer.isOpened()

    def prepare_writing(self, filename):
        """Prepare writing to file

        Args:
            filename (str): the filename

        Returns:
            (bool) If preparation was successful
        """
        if not self._writing:
            if os.path.isfile(filename):
                self._logger.warning(f"File {filename} already exists!")
                return False
            self._writer = cvVideoWriter(filename, self._fourcc, self._fps,
                                         (self._size[0], self._size[1]))
            if self.ready:
                return True
            return False
        else:
            self._logger.info("Already writing")
            return False

    def start_writing(self) -> bool:
        """
        Spawns the writing thread.
        """
        if not self.ready:
            self._logger.warning("Not ready for writing")
            return False

        self._write_thread = WriteThread(self._queue, self._writer, self._fps,
                                         self._size)
        self._write_thread.start()
        self._writing = True
        return True

    def stop_writing(self) -> Tuple[int, float, int]:
        """
        Stop the writing thread returning the number of frames written and
        the total recording time in seconds.
        """
        if not self._writing:
            self._logger.warning("Not writing, nothing to stop")
            return 0, 0.0, 0

        assert self._write_thread is not None

        self._logger.info('Stop writing')
        self._writing = False
        self._write_thread.stop()
        self._write_thread.quit()
        self._write_thread.wait()
        return (self._write_thread.frames_written,
                self._write_thread.recording_time,
                self._write_thread.frames_repeated)

    def release(self):
        if self._writing:
            self.stop_writing()


class WriteThread(QThread):
    """Thread for consuming captured frames.

    This will consume captured frames in variable FPS from a queue and produce
    another queue keeping the frames in the specified frame rate.

    Will skip frames when capturing frame rate is too fast and repeat last
    frame when capturing frame rate is too slow.
    """

    frames_written: int
    frames_repeated: int
    recording_time: int

    def __init__(self, frame_queue: queue.LifoQueue,
                 cv_video_writer: cvVideoWriter, fps: int,
                 size: Tuple[int, int]):
        """Init the WriteThread Object."""
        super().__init__()
        self._queue = frame_queue
        self._towrite_queue: queue.Queue = queue.Queue()
        self._filesystem_writer_thread = QueuedWriterThread(
                self._towrite_queue, cv_video_writer)

        self._stop = False
        self._size = size
        self._frame_duration = 1. / fps
        self._logger = logging.getLogger(__name__ + ".WriteThread")

        self.frames_written = 0
        self.frames_repeated = 0
        self.recording_time = 0

    def stop(self):
        self._filesystem_writer_thread.stop = True
        self._stop = True

    def _write_frame(self, frame: np.array):
        frame_resized = cv2.resize(frame, self._size)
        self._towrite_queue.put(frame_resized)
        self._last_written_frame = frame
        self.frames_written += 1

    def run(self):
        """
        Thread worker for writing frames to queue at quasi constant frame rate.
        """
        self._logger.info("Started writing")
        first_frame_time = 0
        last_frame_time = 0
        frames_repeated = 0

        while first_frame_time == 0 and not self._stop:
            try:
                frame = self._queue.get_nowait()
            except queue.Empty:
                continue
            else:
                first_frame_time = time.time()
                self._write_frame(frame)
                self._filesystem_writer_thread.start()

        while not self._stop:
            calculated_time = (first_frame_time +
                               self.frames_written * self._frame_duration)
            time_difference = calculated_time - time.time()
            if time_difference > 0:
                # if we are ahead of time we should wait
                self._logger.debug(f"Sleeping for {time_difference} seconds")
                time.sleep(time_difference)
            elif time_difference < -self._frame_duration:
                # if we are too late, we should repeat the last frame.
                # this helps when the camera FPS is too slow to keep up with
                # our recording FPS...
                self._logger.debug(f'We are too late, repeat frame')
                frames_repeated += 1
                self._write_frame(self._last_written_frame)
            else:
                # get most recent frame and write it to the file stream
                try:
                    frame = self._queue.get(block=True,
                                            timeout=abs(time_difference))
                except queue.Empty:
                    self._logger.debug(f'Queue empty, no frames available')
                    continue

                self._write_frame(frame)
                last_frame_time = time.time()

            # afterwards discard remaining frames
            skipped_frames = 0
            while not self._queue.empty():
                self._queue.get_nowait()
                self._logger.debug("skipping frame")
                skipped_frames += 1

            if skipped_frames > 0:
                # Frames are skipped when camera capturing FPS is greater
                # than our recording FPS.
                self._logger.debug("skipped %s frames", skipped_frames)

        self._logger.info("Finished writing")
        self.recording_time = last_frame_time - first_frame_time
        self.frames_repeated = frames_repeated
        self._filesystem_writer_thread.wait()


class QueuedWriterThread(QThread):
    """
    Thread for filesystem writing

    Consumes a queue of frames and write to the filesystem.
    """

    stop: bool

    def __init__(self, frame_queue: queue.Queue,
                 cv_video_writer: cvVideoWriter):
        """Init the WriteThread Object."""
        super().__init__()
        self._queue = frame_queue
        self._cv_video_writer = cv_video_writer
        self._logger = logging.getLogger(__name__ + ".QueueCvWriteThread")
        self.stop = False

    def run(self):
        self._logger.info("Starting filesystem writer")
        frames_written = 0
        while not self.stop or not self._queue.empty():
            try:
                frame = self._queue.get(True, 0.1)
            except queue.Empty:
                break
            if self.stop:
                self._logger.info("Waiting for filesystem writer to finish...")
            self._cv_video_writer.write(frame)
            frames_written += 1

        self._logger.info("Releasing cv.VideoWriter")
        self._cv_video_writer.release()
        self._logger.info(
            f"Filesystem writer finished, frames written: {frames_written}")
