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
from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout
from PyQt5.QtCore import QPoint, Qt, QSize
from PyQt5.QtGui import QPainter, QPixmap


class FixedAspectLabel(QLabel):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)

        # Give the frame a border so that we can see it.
        self.setFrameStyle(1)

    def resizeEvent(self, event):
        # Create a square base size of 10x10 and scale it to the new size
        # maintaining aspect ratio.
        new_size = QSize(self.pixmap().size())
        new_size.scale(event.size(), Qt.KeepAspectRatio)
        self.resize(new_size)