"""
    TODO: add file description
"""

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


import logging

from typing import Any, Dict, Optional

from PyQt5.QtCore import QObject, pyqtSignal


class BaseModel(QObject):
    def __new__(cls):
        # Sets a dynamic `_signals` class variable, an array
        # with all attributes emitting signals by this class
        # format is `attribute-name`_changed
        cls._signals = [
            attr[:attr.rfind("_changed")] for attr in
            cls.__dict__.keys() if attr.endswith("_changed") and
            isinstance(getattr(cls, attr), pyqtSignal)]
        return super().__new__(cls)

    def __setattr__(self, attr: Any, value: Any) -> None:
        # Checks if attribute should emit a signal when being set.
        if attr in self._signals:
            getattr(self, attr + "_changed").emit(value)
        return super().__setattr__(attr, value)


class Recorder(BaseModel):
    """
    Stores the current state of capturing and recording, also keeping track
    of number of frames captured and average frame rate.
    """
    is_capturing_changed = pyqtSignal(bool)
    is_recording_changed = pyqtSignal(bool)
    frame_rate_changed = pyqtSignal(float)
    status_msg_changed = pyqtSignal(str)

    is_capturing: bool
    is_recording: bool

    # TODO: it is strange that we keep frame rate and frame counter
    # here but all the math is done by the main controller
    frame_rate: float
    frame_counter: int

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".Recorder")
        self.status_msg = ''
        self.is_capturing = False
        self.is_recording = False

        self.frame_rate = 30.0
        self.frame_counter = 0


class CameraSelectorModel(BaseModel):
    """
    Models the camera selection, responsible for keeping track of cameras
    available to capture from and keeping the current selected camera.
    """
    selection_changed = pyqtSignal(int)
    camera_list_cleared = pyqtSignal()
    camera_removed = pyqtSignal(object)
    camera_added = pyqtSignal(object)

    selection: Optional[int]

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".CameraSelectorModel")
        self._cameras: Dict[int, str] = {}
        self.selection = None

    def add_camera(self, number: int, name: str):
        self._logger.info(f"New camera added: {name} - {number}")
        self._cameras[number] = name
        self.camera_added.emit({'number': number, 'name': name})

    def remove_camera(self, number: int):
        name = self._cameras[number]
        self._logger.info(f"Camera removed: {name} - {number}")
        del self._cameras[number]
        self.camera_removed.emit({'number': number, 'name': name})
