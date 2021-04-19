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

from pyoscvideo.helpers.helpers import cv2qt
from pyoscvideo.video.source_reader import SourceReader


class VideoFile(QObject):
    def __init__(self, filename, control_queue, is_playing=False):
        super().__init__()
        self._logger = logging.getLogger(__name__ + f".VideoFile[{filename}]")
        self._logger.info("Initializing")

        self._control_queue = control_queue
        self._read_queue = queue.LifoQueue()
        self._source_reader = SourceReader(self._read_queue, {})
        self._source_reader.set_source(filename, control_queue)
        self.set_playing(is_playing)
        self._image_update_thread = None
        self._start_image_update_thread()

    def set_playing(self, is_playing):
        self._source_reader.set_video_playing(is_playing)

    def add_change_pixmap_cb(self, callback: Callable[[np.array], None]):
        """
        Sets a function to be called with the current captured frame as
        argument.
        """
        if self._image_update_thread is None:
            self._logger.error("Image update thread is not running")
            return
        self._image_update_thread.change_pixmap.connect(callback)

    def _start_image_update_thread(self):
        """
        Start the capturing of frames.

        Spawns the image update thread.
        """
        if self._image_update_thread:
            self._image_update_thread.stop()

        self._image_update_thread = UpdateVideoImage(self._read_queue)
        self._image_update_thread.start()

    def set_position(self, msecs):
        self._control_queue.put_nowait(msecs)


class UpdateVideoImage(QThread):
    """ Thread for reading frames from the source and updating the image
    """
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
                frame = self._queue.get(timeout=0.1)
            except queue.Empty:
                # TODO: add some warning that we are dropping video frames from
                # video file
                continue
            image = cv2qt(frame)
            self.change_pixmap.emit(image)
