"""video_writer library source code.

video_writer provides a Class for threaded recording from a web cam qt quasi
constant framerate. It uses cv2.VideoCapture and cv2.VideoWriter

    TODO: update description
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

# pylint: disable=trailing-whitespace

import logging
import os
import queue
import time

from PyQt5.QtCore import QThread
from cv2.cv2 import VideoWriter as cvVideoWriter
from cv2.cv2 import VideoWriter_fourcc


def setup_logger():
    """Set up the logger for the module.

    NOTE: Logger needs to be configured from outside the module. See
    "logging_settings.json" in /logging/logs/
    """
    logger = logging.getLogger(__name__)
    logger.info('Logger set up')


class VideoWriter:
    """Video writer class for synchronous video writing to file.

    Arguments:
        queue {queue.LifoQueue} -- The frame_queue
        filename {string} -- The filename
        fourcc {int} -- The fourcc id for the codec options
                        (See: cv2.VideoWriter_fourcc)
        fps {int} -- The desired frame rate
        size {List[int, int]} -- The size of the stream to capture
                                 TODO: check if needed
    """

    def __init__(self, frame_queue, fourcc, frame_rate, size):
        """Init the VideoWriter Object.

        see VideoWriter.__new__
        """
        # pylint: disable=unused-argument
        self._logger = logging.getLogger(__name__ + '.VideoWriter')
        self._logger.info("Initializing")
        if not isinstance(frame_queue, queue.LifoQueue):
            msg = f"Passed argument of wrong type: {type(frame_queue)}"
            self._logger.error(msg)
            raise TypeError(msg)
        self._queue = frame_queue
        # parsing option arguments
        self._ready = False

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
        self._write_thread = None
        # TODO: check if folder exists
        self._stop = False

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if self._writing:
            self._logger.warning("Cannot set size during writing")
        else:
            self._size = value

    @property
    def ready(self):
        """Get the status.

        Returns:
            (bool) if the writer is ready
        """
        return self._ready

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
            if self._writer.isOpened():
                self._ready = True
                return True
            return False
        else:
            self._logger.info("Already writing")
            return False

    def start_writing(self):
        """Start writing.

        Returns:
            (bool) if successful

        """
        if not self._ready:
            self._logger.warning("Not ready for writing")
            return False
        """Start the writing thread."""
        self._write_thread = WriteThread(self._queue, self._writer, self._fps)
        self._write_thread.start()
        self._writing = True
        return True

    def stop_writing(self):
        """Stop the writing thread.

        Returns:
            frames_written (int): the number of frames written
            recording_time (float): the duration of the recording in seconds
        """
        if not self._writing:
            self._logger.warning("Not writing, nothing to stop")
            return 0, 0
        self._logger.info('Stop writing')
        self._writing = False
        self._write_thread.stop = True
        self._write_thread.quit()
        self._write_thread.wait()
        return (self._write_thread.frames_written,
                self._write_thread.recording_time)


class WriteThread(QThread):
    """Class for multi-threaded writing.

    Subclass of QThread.

    """

    def __init__(self, frame_queue, cv_video_writer, fps):
        """Init the WriteThread Object.

        Arguments:
            frame_queue {queue.LifoQueue} -- The queue (Lifo) of frames
                                             to be written
            cv_video_writer {cv.VideoWriter} -- The cv_VideoWriter object for
                                                writing to disk
            fps {int} -- The desired frame rate
        """
        super().__init__()
        if not isinstance(frame_queue, queue.LifoQueue):
            msg = f"Passed argument of wrong type: {type(frame_queue)}"
            self._logger.error(msg)
            raise TypeError(msg)
        self._queue = frame_queue
        self._cv_video_writer = cv_video_writer

        self.stop = False
        self._frames_written = 0
        self._recording_time = 0
        self._frame_duration = 1. / fps
        self._logger = logging.getLogger(__name__ + ".WriteThread")

    def run(self):
        """
        Thread worker for writing frames to queue at quasi constant frame rate.
        """
        self._logger.info("Started writing")
        first_frame_time = 0
        last_frame_time = 0
        while not self.stop:
            calculated_time = (first_frame_time +
                               self._frames_written * self._frame_duration)
            time_difference = calculated_time - time.time()
            # if we are ahead of time we should wait
            if time_difference > 0:
                self._logger.debug("Sleeping for %s seconds", time_difference)
                time.sleep(time_difference)
            else:
                # get most recent frame and write it to the file stream
                try:
                    frame = self._queue.get_nowait()
                except queue.Empty:
                    self._logger.debug('Queue Empty')
                    continue
                # check if frame was read
                if frame is not None:
                    if self._frames_written == 0:
                        first_frame_time = time.time()
                        self._logger.debug("First Frame")
                    if self._cv_video_writer:
                        self._cv_video_writer.write(frame)
                        self._logger.debug("Write frame")
                        self._frames_written += 1
                        last_frame_time = time.time()
                # afterwards discard remaining frames
            skipped_frames = 0
            while self._queue.not_empty:
                try:
                    self._queue.get_nowait()
                except queue.Empty:
                    # exception raised sometimes anyway
                    # check again:
                    if self._queue.empty:
                        break
                self._logger.debug("skipping frame")
                skipped_frames += 1
            if skipped_frames > 0:
                self._logger.warning("skipped %s frames", skipped_frames)

        self._logger.info("Finished writing")
        self._logger.info("Releasing cv.VideoWriter")
        if self._cv_video_writer:
            self._cv_video_writer.release()
        self._recording_time = last_frame_time - first_frame_time

    @property
    def recording_time(self):
        """Get the duration of the recording in seconds.

        Returns:
            float -- the duration of the recording in seconds
        """
        return self._recording_time

    @property
    def frames_written(self):
        """Get the number of written frames.

        Returns:
            int -- The number of written frames
        """
        return self._frames_written
