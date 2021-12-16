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
import glob

import vlc

from threading import Thread, Timer
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import (QMainWindow, QWidget, QFrame, QGridLayout,
                             QFileDialog, QApplication, QLabel,
                             QSizePolicy, QPushButton, QSlider)

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer


class VideoPlayer(QObject):
    """
    Represents the VLC mediaplayer for a video file and the QT Frame
    where to show this video.
    """
    video_ended = pyqtSignal()

    def __init__(self, vlc_instance, video_path):
        super().__init__()
        self._instance = vlc_instance
        self._video_path = video_path
        self._media = self._instance.media_new(video_path)
        self.mediaplayer = self._instance.media_player_new()
        self.mediaplayer.set_media(self._media)
        self.frame = None
        self._init_frame()
        self.mediaplayer.event_manager().event_attach(
                vlc.EventType.MediaPlayerEndReached, self._reload_media)
        self.video_ended.connect(self.reload_media_cb)

    def _init_frame(self):
        """
        Initializes a QFrame object to display the VLC video.
        """
        if not self.frame:
            if sys.platform == "darwin":  # for MacOS
                from PyQt5.QtWidgets import QMacCocoaViewContainer
                self.frame = QMacCocoaViewContainer(0)
            else:
                self.frame = QFrame()
        palette = self.frame.palette()
        palette.setColor(QPalette.Window,
                         QColor(0, 0, 0))
        self.frame.setPalette(palette)
        self.frame.setAutoFillBackground(True)

        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.frame.winId())
        elif sys.platform == "win32":  # for Windows
            self.mediaplayer.set_hwnd(self.frame.winId())
        elif sys.platform == "darwin":  # for MacOS
            self.mediaplayer.set_nsobject(int(frame.winId()))
        self.mediaplayer.play()
        self.mediaplayer.set_pause(True)

    def clean(self):
        self.mediaplayer.stop()
        self.frame.deleteLater()

    def _reload_media(self, event):
        self.video_ended.emit()

    def reload_media_cb(self):
        """
        Releases old media file when it reaches the end and reloads the same
        file.
        """
        self._media.release()
        self._media = self._instance.media_new(self._video_path)
        self.mediaplayer.set_media(self._media)

    def get_length(self):
        return self.mediaplayer.get_length()


class Player(QMainWindow):
    """
    The main window of the pyOscVideoPlayer, also holds the OSC server thread.
    """
    def __init__(self, address='127.0.0.1', port=57221, use_osc=True):
        QMainWindow.__init__(self)
        self.setWindowTitle("pyOscVideo Player")

        self.use_osc = use_osc
        self.instance = vlc.Instance()
        self.videos = []
        self._is_playing = False

        self.info = None
        self.play_button = None
        self.load_button = None
        self.position_slider = None
        self._position_tracker = None

        self._create_ui()
        self.isPaused = False

        if self.use_osc:
            self.osc_server = OSCServer(address, port)
            self.osc_server.play_message.connect(self.play)
            self.osc_server.pause_message.connect(self.pause)
            self.osc_server.add_video_message.connect(self.add_video)
            self.osc_server.clean_message.connect(self.clean)
            self.osc_server.set_time_message.connect(self.set_time)
            self.osc_server.start()

    @property
    def _max_length(self):
        if not self.videos:
            return 0
        n = max([player.get_length() for player in self.videos])
        return n

    def close(self):
        """
        Stops the position tracker and frees all loaded videos.
        """
        if self._position_tracker:
            self._position_tracker.cancel()
        self.clean()

    def _create_ui(self):
        """
        Creates the main window with a GridLayout to add videos to.
        """
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.gridlayout = QGridLayout()
        self.widget.setLayout(self.gridlayout)
        self._skip_lines = 0

        if self.use_osc:
            self.info = QLabel("Waiting for OSC message...")
            self.info.setSizePolicy(QSizePolicy.Expanding,
                                    QSizePolicy.Expanding)
            self.info.setAlignment(Qt.AlignCenter)
            self.gridlayout.addWidget(self.info)
        else:
            self.play_button = QPushButton("Play")
            self.play_button.clicked.connect(self._button_play)
            self.load_button = QPushButton("Load folder")
            self.load_button.clicked.connect(self._choose_folder)
            self.position_slider = QSlider(Qt.Horizontal)
            self.position_slider.setMinimum(0)
            self.position_slider.setMaximum(10000)
            self.position_slider.sliderMoved.connect(
                    lambda value: self.set_time(
                        int((value/10000)*self._max_length)))
            self.position_slider.setSingleStep(0.1)
            self.gridlayout.addWidget(self.load_button, 0, 0)
            self.gridlayout.addWidget(self.play_button, 0, 1)
            self.gridlayout.addWidget(self.position_slider, 1, 0, 1, -1)
            self._skip_lines = 2
            self.info = QLabel("Waiting for videos...")
            self.info.setSizePolicy(
                    QSizePolicy.Expanding,
                    QSizePolicy.Expanding)
            self.info.setAlignment(Qt.AlignCenter)
            self.gridlayout.addWidget(self.info, self._skip_lines, 0, -1, -1)
            self._position_tracker = Timer(0.5, self._set_position_slider)
            self._position_tracker.start()

    def _set_position_slider(self):
        if self.videos:
            current_time = self.videos[0].mediaplayer.get_time()
            self.position_slider.setValue(
                    (current_time / (self._max_length))*10000)
        self._position_tracker = Timer(0.5, self._set_position_slider)
        self._position_tracker.start()

    def _button_play(self):
        self.play_button.clicked.disconnect(self._button_play)
        self.play_button.clicked.connect(self._button_pause)
        self.play_button.setText("Pause")
        self.play()

    def _button_pause(self):
        self.play_button.clicked.disconnect(self._button_pause)
        self.play_button.clicked.connect(self._button_play)
        self.play_button.setText("Play")
        self.pause()

    def _choose_folder(self):
        self.clean()
        self.add_folder(str(QFileDialog.getExistingDirectory(
            self, "Select folder")))

    def add_folder(self, folder_path):
        """
        Loads all .mov videos from the specified folder.
        """
        for video in glob.glob(os.path.join(folder_path, "*.mov")):
            self.add_video(video)

    def add_video(self, video_path):
        """
        Loads video file from video_path.
        """
        if self.info:
            self.info.hide()
            self.info = None
        player = VideoPlayer(self.instance, video_path)
        self.gridlayout.addWidget(
                player.frame,
                self._skip_lines + len(self.videos) // 2, len(self.videos) % 2)
        self.videos.append(player)

    def clean(self):
        """
        Unloads all videos and remove them from the UI.
        """
        if self.position_slider:
            if self._is_playing:
                self._button_pause()
            self.position_slider.setValue(0)

        for player in self.videos:
            self.gridlayout.removeWidget(player.frame)
            player.clean()
            del player

        self.videos = []

    def play(self):
        """
        Plays all videos.
        """
        for video in self.videos:
            video.mediaplayer.play()
        self._is_playing = True

    def pause(self):
        """
        Pauses all videos.
        """
        for video in self.videos:
            video.mediaplayer.pause()
        self._is_playing = False

    def set_time(self, time):
        """
        Sets time as an integer in milliseconds.
        """
        for video in self.videos:
            video.mediaplayer.set_time(time)


class OSCServer(QThread):
    """
    Thread worker for the OSC server
    """
    add_video_message = pyqtSignal(str)
    play_message = pyqtSignal()
    pause_message = pyqtSignal()
    clean_message = pyqtSignal()
    set_time_message = pyqtSignal(int)

    def __init__(self, address="localhost", port=57221):
        self.address = address
        self.port = port
        super().__init__()

    def add_video(self, address, filepath):
        # Emits the add_video_message signal
        self.add_video_message.emit(filepath)

    def add_folder(self, address, folderpath):
        # Emits the add_video_message signal for each file in video folder
        videos = glob.glob(os.path.join(folderpath, "*.mov"))
        for video in videos:
            self.add_video_message.emit(video)

    def play(self, address):
        # Emits the play_message signal
        self.play_message.emit()

    def pause(self, address):
        # Emits the pause_message signal
        self.pause_message.emit()

    def set_time(self, address, time):
        # Emits the position_message signal
        self.set_time_message.emit(time)

    def clean(self, address):
        # Emits the clean_message signal
        self.clean_message.emit()

    def run(self):
        """
        Initialize the OSC server and starts serving.
        """
        dispatcher = Dispatcher()
        dispatcher.map("/oscVideo/setVideoPlay", self.play)
        dispatcher.map("/oscVideo/setVideoPause", self.pause)
        dispatcher.map("/oscVideo/setVideoPosition", self.set_time)
        dispatcher.map("/oscVideo/loadFile", self.add_video)
        dispatcher.map("/oscVideo/loadFolder", self.add_folder)
        dispatcher.map("/oscVideo/clean", self.clean)

        server = BlockingOSCUDPServer((self.address, self.port), dispatcher)
        server.serve_forever()


def main_player():
    """Start the Player application."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', default="127.0.0.1",
                        help="Address to listen for OSC messages")
    parser.add_argument('-p', '--port', default=57221,
                        help="Port to listen for OSC messages")
    parser.add_argument('-n', '--no-osc', const=True, dest='no_osc',
                        action='store_const',
                        help="Disables OSC controller, enable GUI controls")
    parsed_args, unparsed_args = parser.parse_known_args()
    app = QApplication(sys.argv)
    player = Player(parsed_args.address, parsed_args.port,
                    not parsed_args.no_osc)
    player.show()
    player.resize(1280, 960)
    app.aboutToQuit.connect(player.close)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main_player()
