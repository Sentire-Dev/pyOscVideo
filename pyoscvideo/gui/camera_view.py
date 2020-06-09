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
from typing import List, Optional

import numpy as np
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QLabel, QSizePolicy, QComboBox,
                             QHBoxLayout, QVBoxLayout, QWidget)

from pyoscvideo.video.manager import VideoManager
from pyoscvideo.gui.camera_view_ui import Ui_CameraView
from pyoscvideo.gui.main_view_ui import Ui_MainWindow
from pyoscvideo.video.camera import Camera


class CameraView(QWidget):
    """
    CameraView is responsible for constructing the UI for a camera and
    setup the callbacks for updating the image, fps and which camera to
    use.
    """
    _camera: Optional[Camera]

    def __init__(self, video_manager: VideoManager, ui: Ui_MainWindow,
                 camera: Optional[Camera] = None):
        """
        Sets up the widgets and layouts for a camera in the UI and bind UI
        actions.
        """

        super().__init__()

        self._logger = logging.getLogger(
            __name__ + f".CameraView")
        self._logger.info("Initializing")
        self._ui = Ui_CameraView()
        self._ui.setupUi(self)
        self._video_manager = video_manager

    #     self.layout = vlayout
    #     self._ui.frameRateLabel = fps_label
    #     self._ui.cameraSelectionComboBox = combo_box
    #     self._ui.imageLabel = label
        self._camera = camera
    #
        self._init_image_label()
    #
        self._camera_list: List[Camera] = []

        self._ui.cameraSelectionComboBox.insertItem(0, "No camera")
        for camera in self._video_manager.camera_selector.cameras.values():
            self._add_camera_combo_box(camera)

        if self._camera is not None:
            self._ui.cameraSelectionComboBox.setCurrentIndex(
                self._camera_list.index(self._camera) + 1)

        video_manager.is_recording_changed.connect(
                self._update_recording)
        self._update_recording(video_manager.is_recording)

        self._bind_actions()
        self._start_capturing()

    def _update_recording(self, is_recording: bool):
        self._ui.cameraSelectionComboBox.setEnabled(not is_recording)

    def _bind_actions(self):
        """
        Binds UI and model state changes together.
        """
        self._ui.cameraSelectionComboBox.currentIndexChanged.connect(
            self._change_current_camera)

        self._video_manager.camera_selector.camera_added.connect(
            self._add_camera_combo_box)
        self._video_manager.camera_selector.camera_removed.connect(
            self._remove_camera_combo_box)

    def _init_image_label(self):
        """
        Initializes the image placeholder when there's no camera selected.
        """
        black_pixmap = QPixmap(400, 300)
        black_pixmap.fill(Qt.black)
        self._ui.imageLabel.setPixmap(black_pixmap)

    def _start_capturing(self):
        """
        Notifies the video manager that we want to use this camera, so
        it should start capturing.
        """
        if self._camera:
            if not self._video_manager.use_camera(self._camera):
                self._logger.warning(f"Failed to use '{self._camera.name}'")
                self._camera = None
                return
            self._camera.add_change_pixmap_cb(self._on_new_frame)
            self._camera.add_update_fps_label_cb(self._update_fps_label)

    def _update_fps_label(self, fps: float):
        """
        Callback to update the FPS text label.
        """
        self._ui.frameRateLabel.setText("Fps: " + str(round(fps, 1)))

        assert self._camera is not None

        if self._camera.recording_fps > fps:
            self._ui.frameRateLabel.setStyleSheet('color: red')
        else:
            self._ui.frameRateLabel.setStyleSheet('color: black')

    def _add_camera_combo_box(self, camera: Camera):
        """
        Called when a new camera is reported by the CameraSelector.
        """
        self._camera_list.append(camera)
        self._camera_list.sort(key=lambda e: e.name)
        idx = self._camera_list.index(camera) + 1
        self._ui.cameraSelectionComboBox.insertItem(idx, camera.name)

    def _remove_camera_combo_box(self, camera: Camera):
        """
        Called when a camera removal is reported by the CameraSelector.
        """
        idx = self._camera_list.index(camera)
        del self._camera_list[idx]
        self._ui.cameraSelectionComboBox.removeItem(idx + 1)

    def _change_current_camera(self, index: int):
        """
        Called when the user changes the camera monitored by this CameraView.
        """
        self._logger.info(f"Changing current camera to index: {index}")
        self.cleanup()

        if index == 0:
            self._camera = None
            self._init_image_label()
            return

        self._camera = self._camera_list[index - 1]
        self._start_capturing()

    def _on_new_frame(self, image: np.array):
        """
        Set the image in the main window.
        """
        self._ui.imageLabel.setPixmap(QPixmap.fromImage(image).scaled(
            self._ui.imageLabel.size(),
            Qt.KeepAspectRatio,
            Qt.FastTransformation))

    def cleanup(self):
        """
        Releases all the callbacks and report to the manager we no longer use
        the camera.
        """
        if self._camera:
            self._camera.remove_change_pixmap_cb(self._on_new_frame)
            self._camera.remove_update_fps_label_cb(self._update_fps_label)
            self._video_manager.unuse_camera(self._camera)
