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
        QHBoxLayout, QVBoxLayout, QPushButton)
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt, QSize
from PyQt5.QtGui import QPixmap, QImage

from pyoscvideo.video.manager import VideoManager
from pyoscvideo.video.camera import Camera
from pyoscvideo.gui.main_view_ui import Ui_MainWindow
from pyoscvideo.gui.camera_view import CameraView


class MainView(QMainWindow):
    """
    The main Window
    """
    should_quit = pyqtSignal()

    def __init__(self, video_manager: VideoManager, num_cameras: int = 1):
        super().__init__()
        self._logger = logging.getLogger(__name__+".MainView")

        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        self.should_quit.connect(video_manager.cleanup)

        self._camera_views: List[CameraView] = []
        self._video_manager = video_manager

        # for now shows / uses all cameras available
        for i in range(num_cameras):
            self._add_camera_view()

        self._ui.recordButton.clicked.connect(video_manager.toggle_recording)

        video_manager.status_msg_changed.connect(self._set_status_msg)
        video_manager.is_recording_changed.connect(
                self._update_recording)

        video_manager.is_capturing_changed.connect(
                self._update_capturing)
        self._update_capturing(self._video_manager.is_capturing)

        self.setStatusBar(self._ui.statusbar)

    def _add_camera_view(self):
        """
        Adds a camera view to the camera grid.
        """
        camera_view = CameraView(self._video_manager, self._remove_camera_view)
        self._camera_views.append(camera_view)
        camera_view.show()
        num_layouts = self._ui.camerasLayout.count()
        self._ui.camerasLayout.addWidget(camera_view)
        self._update_camera_layout()

    def _update_camera_layout(self):
        """
        Updates the camera grid layout in order to ensure equal sizes for the
        camera views.
        """
        for i in range(self._ui.camerasLayout.columnCount()):
            self._ui.camerasLayout.setColumnStretch(i, 1)

        for j in range(self._ui.camerasLayout.rowCount()):
            self._ui.camerasLayout.setRowStretch(j, 1)

    def _remove_camera_view(self, camera_view):
        """
        Removes a camera view from the camera grid.
        """
        # TODO: check which layout is better to display the
        # cameras, because you can't dynamically update
        # the positions with grid layout. For now
        # we use this recursive hack to remove all elements
        # from the cameraview layout
        def recursive_remove_view(layout):
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        layout.removeWidget(widget)
                        widget.deleteLater()
                    else:
                        recursive_remove_view(item.layout())

        recursive_remove_view(camera_view.layout)

    @pyqtSlot(bool)
    def _update_capturing(self, is_capturing: bool):
        """
        Updates the GUI record button, cant record if isn't capturing.
        """
        self._ui.recordButton.setEnabled(is_capturing)

    @pyqtSlot(bool)
    def _update_recording(self, is_recording: bool):
        """
        Updates the GUI accordingly to the current recording state.
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
            if self._video_manager.is_recording:
                confirm = QMessageBox.warning(
                    self,
                    'Message',
                    "You are currently recording, "
                    "are you sure you want to quit?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                if confirm == QMessageBox.No:
                    event.ignore()
                    return

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
