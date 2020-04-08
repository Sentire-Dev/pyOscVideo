"""
Main View
TODO: add proper description
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
import queue
import time
import numpy as np

from typing import Any, Dict, List

from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QImage

from pyoscvideo.controllers.main_ctrl import MainController
from pyoscvideo.gui.main_view_ui import Ui_MainWindow


class MainView(QMainWindow):
    """ The main Window
    """
    should_quit = pyqtSignal()

    def __init__(self, controller: MainController):
        super().__init__()
        self._logger = logging.getLogger(__name__+".MainView")

        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)

        self._controller = controller
        self._model = self._controller._model
        self._camera_selector_model = self._controller._camera_selector._model

        self._camera_list: List[dict] = []

        # Connect signals from controller to update the interface dynamically
        self._camera_selector_model.camera_added.connect(
                self._add_camera_comboBox)
        self._camera_selector_model.camera_removed.connect(
                self._remove_camera_comboBox)
        self._camera_selector_model.selection_changed.connect(
                self._current_camera_changed)

        self._controller.set_update_fps_label_cb(self._update_fps_label)
        self._model.status_msg_changed.connect(self._set_status_msg)
        self._model.is_recording_changed.connect(self._update_recording_button)

        # Connect actions in UI to the controller
        self._ui.camera_selection_comboBox.currentIndexChanged.connect(
                self._change_current_camera)
        self._ui.recordButton.clicked.connect(
                self._controller.toggle_recording)
        self.should_quit.connect(self._controller.cleanup)

        for number, name in self._camera_selector_model._cameras.items():
            self._add_camera_comboBox({'number': number, 'name': name})

        self.setStatusBar(self._ui.statusbar)

    @pyqtSlot(bool)
    def _update_recording_button(self, is_recording: bool):
        if self._ui.recordButton.isChecked() != is_recording:
            self._ui.recordButton.toggle()

    @pyqtSlot(int)
    def _change_current_camera(self, index: int):
        number = self._camera_list[index]['number']
        self._logger.info(f"Changing current camera to: {index}")
        self._camera_selector_model.selection = (
                self._camera_list[index]['number'])

    @pyqtSlot(int)
    def _current_camera_changed(self, device_id: int):
        self._logger.info(f"Current camera changed to {device_id}")
        try:
            device_info = {
                'number': device_id,
                'name': self._camera_selector_model._cameras[device_id]
                }
        except KeyError:
            self._logger.warning(
                    f"Tried to choose an invalid camera with id: {device_id}")
            return

        idx = self._camera_list.index(device_info)
        if idx != self._ui.camera_selection_comboBox:
            # check if we need to update ourselves
            self._ui.camera_selection_comboBox.setCurrentIndex(idx)
            self._controller.set_change_pixmap_cb(self._on_new_frame)

    @pyqtSlot(object)
    def _add_camera_comboBox(self, camera_info: Dict[str, Any]):
        self._camera_list.append(camera_info)
        self._camera_list.sort(key=lambda e: e['number'])
        idx = self._camera_list.index(camera_info)
        self._ui.camera_selection_comboBox.insertItem(idx, camera_info['name'])

    @pyqtSlot(object)
    def _remove_camera_comboBox(self, camera_info: Dict[str, Any]):
        idx = self._camera_list.index(camera_info)
        del self._camera_list[idx]
        self._ui.camera_selection_comboBox.removeItem(idx)

    @pyqtSlot(str)
    def _set_status_msg(self, msg: str):
        self._ui.statusbar.setEnabled(True)
        self._logger.debug("Status changed: %s", msg)
        self._ui.statusbar.showMessage(msg)

    @pyqtSlot(QImage)
    def _on_new_frame(self, image: np.array):
        """
        Set the image in the main window.
        """
        self._logger.debug("New frame")
        self._ui.imageLabel.setPixmap(QPixmap.fromImage(image).scaled(
            self._ui.imageLabel.size(),
            Qt.KeepAspectRatio,
            Qt.FastTransformation))

    @pyqtSlot(float)
    def _update_fps_label(self, fps: float):
        self._ui.frame_rate_label.setText("Fps: " + str(round(fps, 1)))

    def closeEvent(self, event):
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
        self.should_quit.emit()
