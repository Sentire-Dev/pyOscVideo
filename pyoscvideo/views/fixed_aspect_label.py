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
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QPoint, Qt, QSize
from PyQt5.QtGui import QPainter, QPixmap


class FixedAspectLabel(QLabel):
    def paintEvent(self, event):
        size = self.size()
        painter = QPainter(self)
        point = QPoint(0, 0)
        if isinstance(self.pixmap(), QPixmap):
            scaled_pixmap = self.pixmap().scaled(size, Qt.KeepAspectRatio, transformMode=Qt.FastTransformation)
            self.setMaximumSize(scaled_pixmap.size())
            point.setX(0)
            point.setY(0)
            # print (point.x(), ' ', point.y())
            painter.drawPixmap(point, scaled_pixmap)
            self.setMaximumSize(QSize(4000, 5000))
