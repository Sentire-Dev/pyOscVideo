# *****************************************************************************
#  Copyright (c) 2021. Pascal Staudt, Bruno Gola                              *
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


import sys
import os.path
import argparse
import vlc

from threading import Thread
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import (QMainWindow, QWidget, QFrame, QGridLayout,
                             QApplication)

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


class VideoPlayer:
    """
    Represents the VLC mediaplayer for a video file and the QT Frame
    where to show this video.
    """
    def __init__(self, mediaplayer):
        self.mediaplayer = mediaplayer

        if sys.platform == "darwin":  # for MacOS
            from PyQt5.QtWidgets import QMacCocoaViewContainer
            frame = QMacCocoaViewContainer(0)
        else:
            frame = QFrame()
        palette = frame.palette()
        palette.setColor(QPalette.Window,
                         QColor(0, 0, 0))
        frame.setPalette(palette)
        frame.setAutoFillBackground(True)

        self.frame = frame

        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.frame.winId())
        elif sys.platform == "win32":  # for Windows
            self.mediaplayer.set_hwnd(self.frame.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.mediaplayer.set_nsobject(int(frame.winId()))


class Player(QMainWindow):
    """
    The main window of the pyOscVideoPlayer, also holds the OSC server thread.
    """
    def __init__(self, address='127.0.0.1', port=42424):
        QMainWindow.__init__(self)
        self.setWindowTitle("pyOscVideo Player")

        self.instance = vlc.Instance()
        self.videos = []

        self.create_ui()
        self.isPaused = False
        self.osc_server = OSCServer()
        self.osc_server.play_message.connect(self.play)
        self.osc_server.pause_message.connect(self.pause)
        self.osc_server.add_video_message.connect(self.add_video)
        self.osc_server.set_time_message.connect(self.set_time)
        self.osc_server.address = address
        self.osc_server.port = port
        self.osc_server.start()

    def create_ui(self):
        """
        Creates the main window with a GridLayout to add videos to.
        """
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.gridlayout = QGridLayout()
        self.widget.setLayout(self.gridlayout)

    def add_video(self, videoPath):
        player = VideoPlayer(self.instance.media_player_new(videoPath))
        self.gridlayout.addWidget(player.frame,
                                  len(self.videos) // 2, len(self.videos) % 2)
        self.videos.append(player)

    def play(self):
        for video in self.videos:
            video.mediaplayer.play()

    def pause(self):
        for video in self.videos:
            video.mediaplayer.pause()

    def set_time(self, time):
        for video in self.videos:
            video.mediaplayer.set_time(time)


class OSCServer(QThread):
    """
    Thread worker for the OSC server
    """
    add_video_message = pyqtSignal(str)
    play_message = pyqtSignal()
    pause_message = pyqtSignal()
    set_time_message = pyqtSignal(int)

    def __init__(self):
        self.address = "127.0.0.1"
        self.port = 42424
        super().__init__()

    def add_video(self, address, filepath):
        # Emits the add_video_message signal
        self.add_video_message.emit(filepath)

    def play(self, address):
        # Emits the play_message signal
        self.play_message.emit()

    def pause(self, address):
        # Emits the pause_message signal
        self.pause_message.emit()

    def set_time(self, address, time):
        # Emits the position_message signal
        self.set_time_message.emit(time)

    def run(self):
        """
        Initialize the OSC server and starts serving.
        """
        dispatcher = Dispatcher()
        dispatcher.map("/oscVideo/setVideoPlay", self.play)
        dispatcher.map("/oscVideo/setVideoPause", self.pause)
        dispatcher.map("/oscVideo/setVideoPosition", self.set_time)
        dispatcher.map("/oscVideo/loadFile", self.add_video)

        server = BlockingOSCUDPServer((self.address, self.port), dispatcher)
        server.serve_forever()


def main_player():
    """Start the Player application."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default="127.0.0.1",
                        help="Address to listen for OSC messages")
    parser.add_argument('-p', '--port', default=42424,
                        help="Port to listen for OSC messages")
    parsed_args, unparsed_args = parser.parse_known_args()
    app = QApplication(sys.argv)
    player = Player(parsed_args.address, parsed_args.port)
    player.show()
    player.resize(1280, 960)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main_player()
