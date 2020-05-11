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
import queue
import time
import numpy as np

from typing import Any, Callable, Dict, List, Optional

from PyQt5.QtWidgets import (
        QMainWindow, QMessageBox, QLabel, QSizePolicy, QComboBox,
        QHBoxLayout, QVBoxLayout)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt, QSize
from PyQt5.QtGui import QPixmap, QImage

from pyoscvideo.controllers.main_ctrl import MainController
from pyoscvideo.video.camera import Camera
from pyoscvideo.video.camera_selector import CameraSelector
from pyoscvideo.gui.main_view_ui import Ui_MainWindow
from pyoscvideo.gui.camera_view import CameraView


class MainView(QMainWindow):
    """
    The main Window
    """
    should_quit = pyqtSignal()

    def __init__(self, main_controller):
        super().__init__()
        self._logger = logging.getLogger(__name__+".MainView")

        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        self.should_quit.connect(main_controller.cleanup)

        self._camera_views = []

        # for now shows / uses all cameras available
        for i, camera in enumerate(CameraSelector.cameras.values()):
            self._logger.info("Adding Camera View")
            camera_view = CameraView(main_controller, self._ui.camerasLayout)
            camera_view.show()
            self._camera_views.append(camera_view)
            self._ui.camerasLayout.addWidget(camera_view)

        self._ui.recordButton.clicked.connect(
            main_controller.toggle_recording)

        main_controller._model.status_msg_changed.connect(self._set_status_msg)
        main_controller._model.is_recording_changed.connect(
                self._update_recording_button)

        self.setStatusBar(self._ui.statusbar)

    @pyqtSlot(bool)
    def _update_recording_button(self, is_recording: bool):
        """
        Updates the recording button to the current recording state.
        """
        if self._ui.recordButton.isChecked() != is_recording:
            self._ui.recordButton.toggle()

    @pyqtSlot(str)
    def _set_status_msg(self, msg: str):
        """
        Called when there is a new satus message.
        Sets the message in the status bar.
        """
        self._ui.statusbar.setEnabled(True)
        self._logger.debug("Status changed: %s", msg)
        self._ui.statusbar.showMessage(msg)

    def closeEvent(self, event):
        """
        Called when user tries to close the window, shows confirmation dialog.
        """
        reply = QMessageBox.question(
                self,
                'Message',
                "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.on_quit()
            event.accept()
        else:
            event.ignore()

    def on_quit(self):
        """
        Cleans up the state, releasing all cameras before quitting.
        """
        for camera_view in self._camera_views:
            camera_view.cleanup()
        self.should_quit.emit()
