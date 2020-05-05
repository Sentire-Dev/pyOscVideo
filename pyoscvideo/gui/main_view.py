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
from pyoscvideo.video.camera_selector import CameraSelector
from pyoscvideo.gui.main_view_ui import Ui_MainWindow


class CameraView:
    """
    CameraView is responsible for constructing the UI for a camera and
    setup the callbacks for updating the image, fps and which camera to
    use.
    """
    def __init__(self, video_manager: VideoManager,
                 on_close: Callable, camera: Optional[Camera] = None):
        """
        Sets up the widgets and layouts for a camera in the UI and bind UI
        actions.
        """
        self._video_manager = video_manager
        self._logger = logging.getLogger(
                __name__+f".CameraView")
        self._on_close = on_close
        vlayout = QVBoxLayout()
        label = QLabel()
        label.setEnabled(True)
        sp = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        sp.setHorizontalStretch(0)
        sp.setVerticalStretch(0)
        sp.setHeightForWidth(label.sizePolicy().hasHeightForWidth())
        label.setSizePolicy(sp)
        label.setMinimumSize(QSize(1, 1))
        label.setSizeIncrement(QSize(0, 0))
        label.setLayoutDirection(Qt.LeftToRight)
        label.setScaledContents(False)
        label.setAlignment(Qt.AlignCenter)
        vlayout.addWidget(label)

        hlayout = QHBoxLayout()
        combo_box = QComboBox()

        fps_label = QLabel()
        sp_fps = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sp_fps.setHorizontalStretch(0)
        sp_fps.setVerticalStretch(0)
        sp_fps.setHeightForWidth(fps_label.sizePolicy().hasHeightForWidth())
        fps_label.setSizePolicy(sp_fps)
        fps_label.setLayoutDirection(Qt.LeftToRight)
        fps_label.setAlignment(Qt.AlignCenter)
        close_button = QPushButton()
        close_button.setText("Close")
        close_button.clicked.connect(self._close)
        hlayout.addWidget(combo_box)
        hlayout.addWidget(fps_label)
        hlayout.addWidget(close_button)
        vlayout.addLayout(hlayout)

        self.layout = vlayout
        self._fps_label = fps_label
        self._combo_box = combo_box
        self._image_label = label
        self._camera = camera

        self._init_image_label()

        self._camera_list: List[Camera] = []

        self._combo_box.insertItem(0, "------")
        for camera in CameraSelector.cameras.values():
            self._add_camera_combo_box(camera)

        if self._camera is not None:
            self._combo_box.setCurrentIndex(
                    self._camera_list.index(self._camera) + 1)

        self._bind_actions()
        self._start_capturing()

    def _bind_actions(self):
        self._combo_box.currentIndexChanged.connect(
            self._change_current_camera)

        CameraSelector.camera_added.connect(
                self._add_camera_combo_box)
        CameraSelector.camera_removed.connect(
                self._remove_camera_combo_box)

    def _init_image_label(self):
        black_pixmap = QPixmap(400, 300)
        black_pixmap.fill(Qt.black)
        self._image_label.setPixmap(black_pixmap)

    def _start_capturing(self):
        if self._camera:
            if not self._video_manager.use_camera(self._camera):
                self._logger.warning(f"Failed to use '{self._camera.name}'")
                self._camera = None
                return
            self._camera.add_change_pixmap_cb(self._on_new_frame)
            self._camera.add_update_fps_label_cb(self._update_fps_label)

    def _update_fps_label(self, fps: float):
        self._fps_label.setText("Fps: " + str(round(fps, 1)))

    def _add_camera_combo_box(self, camera: Camera):
        self._camera_list.append(camera)
        self._camera_list.sort(key=lambda e: e.name)
        idx = self._camera_list.index(camera) + 1
        self._combo_box.insertItem(idx, camera.name)

    def _remove_camera_combo_box(self, camera: Camera):
        idx = self._camera_list.index(camera)
        del self._camera_list[idx]
        self._combo_box.removeItem(idx + 1)

    def _change_current_camera(self, index: int):
        self._logger.info(f"Changing current camera to index: {index}")
        self.cleanup()

        if index == 0:
            self._camera = None
            return

        self._camera = self._camera_list[index - 1]
        self._start_capturing()

    def _on_new_frame(self, image: np.array):
        """
        Set the image in the main window.
        """
        self._image_label.setPixmap(QPixmap.fromImage(image).scaled(
            self._image_label.size(),
            Qt.KeepAspectRatio,
            Qt.FastTransformation))

    def _close(self):
        self.cleanup()
        self._on_close(self)

    def cleanup(self):
        if self._camera:
            self._camera.remove_change_pixmap_cb(self._on_new_frame)
            self._camera.remove_update_fps_label_cb(self._update_fps_label)
            self._video_manager.unuse_camera(self._camera)


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
        self._ui.addCamera.clicked.connect(self._add_camera_view)
        self._ui.recordingFPS.valueChanged.connect(
                self._video_manager.set_recording_fps)

        video_manager.status_msg_changed.connect(self._set_status_msg)
        video_manager.is_recording_changed.connect(
                self._update_recording_button)

        self._ui.recordingFPS.setValue(
                video_manager.camera_options['recording_fps'])
        self.setStatusBar(self._ui.statusbar)

    def _add_camera_view(self):
        """
        Adds a camera view to the camera grid.
        """
        camera_view = CameraView(self._video_manager, self._close_camera_view)
        self._camera_views.append(camera_view)
        num_layouts = self._ui.camerasLayout.count()
        self._ui.camerasLayout.addLayout(
                camera_view.layout, num_layouts // 2, num_layouts % 2)

    def _close_camera_view(self, camera_view):
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
    def _update_recording_button(self, is_recording: bool):
        if self._ui.recordButton.isChecked() != is_recording:
            self._ui.recordButton.toggle()

    @pyqtSlot(str)
    def _set_status_msg(self, msg: str):
        self._ui.statusbar.setEnabled(True)
        self._logger.debug("Status changed: %s", msg)
        self._ui.statusbar.showMessage(msg)

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
        for camera_view in self._camera_views:
            camera_view.cleanup()
        self.should_quit.emit()
