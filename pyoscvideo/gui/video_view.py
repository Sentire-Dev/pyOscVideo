from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap

from pyoscvideo.gui.video_view_ui import Ui_VideoView

import numpy as np
import logging


class VideoView(QWidget):
    """
    A window to display a video
    """
    should_quit = pyqtSignal()

    def __init__(self, video):
        super().__init__()
        self._logger = logging.getLogger(__name__+".VideoView")

        self._ui = Ui_VideoView()
        self._ui.setupUi(self)
        self._video = video
        self._init_image_label()
        self._video.add_change_pixmap_cb(self._on_new_frame)

    def _init_image_label(self):
        """
        Initializes the image placeholder when there's no camera selected.
        """
        black_pixmap = QPixmap(400, 300)
        black_pixmap.fill(Qt.black)
        self._ui.imageLabel.setPixmap(black_pixmap)

    def _on_new_frame(self, image: np.array):
        """
        Set the image in the main window.
        """
        self._ui.imageLabel.setPixmap(QPixmap.fromImage(image).scaled(
            self._ui.imageLabel.size(),
            Qt.KeepAspectRatio,
            Qt.FastTransformation))
