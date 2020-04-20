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
    def __new__(cls, *args, **kwargs):
        # Sets a dynamic `_signals` class variable, an array
        # with all attributes emitting signals by this class
        # format is `attribute-name`_changed
        cls._signals = [
            attr[:attr.rfind("_changed")] for attr in
            cls.__dict__.keys() if attr.endswith("_changed") and
            isinstance(getattr(cls, attr), pyqtSignal)]
        return super().__new__(cls, *args, **kwargs)

    def __setattr__(self, attr: Any, value: Any) -> None:
        # Checks if attribute should emit a signal when being set.
        if attr in self._signals:
            getattr(self, attr + "_changed").emit(value)
        return super().__setattr__(attr, value)


class MainModel(BaseModel):
    """
    Stores the current state of capturing and recording, also keeping track
    of number of frames captured and average frame rate.
    """
    is_recording_changed = pyqtSignal(bool)
    status_msg_changed = pyqtSignal(str)

    is_recording: bool

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".Recorder")
        self.status_msg = ''
        self.is_recording = False
