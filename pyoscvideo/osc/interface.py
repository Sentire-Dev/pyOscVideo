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


from typing import Any, Sequence, Type

from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient

from PyQt5.QtCore import QThread

from pyoscvideo.video.manager import VideoManager

import asyncio
import logging


class OSCInterface(QThread):
    """
    Spawns a thread for sending and receiving OSC messages to
    stop and start the recorder.
    """
    def __init__(self,
                 video_manager: VideoManager,
                 address: str = "0.0.0.0",
                 port: int = 57220,
                 remote_address: str = "127.0.0.1",
                 remote_port: int = 57120
                 ):
        super().__init__()
        self._logger = logging.getLogger(__name__+".OSCInterface")
        self._logger.info("Initializing OSC thread")
        self._video_manager = video_manager
        self._address = address
        self._port = port
        self._remote_address = remote_address
        self._remote_port = remote_port

        self.server: ThreadingOSCUDPServer = None
        self.client: SimpleUDPClient = None

    def _send_message(self, path: str, args: Sequence[Any]):
        self._logger.info(
                f"Sending message '{path}' with args '{args}' to client")
        self.client.send_message(path, args)

    def _prepare_recording(self, addr: str, filename: str = ""):
        self._logger.info(
                f"Prepare recording with filename: {filename}")
        if filename == "":
            self._logger.warning("No filename argument")
            self._send_message("/oscVideo/status",
                               (False, "No filename provided"))
        elif self._video_manager.prepare_recording(filename):
            self._send_message("/oscVideo/status",
                               (True, "Prepared Recording"))
        else:
            self._send_message("/oscVideo/status",
                               (False, "Could not prepare Recording"))

    def _record(self, addr: str, record: bool):
        if record is None:
            self._logger.warning(f"No argument sent, expecting "
                                 f"a boolean to start or stop recording")
        elif record:
            if self._video_manager.start_recording():
                self._send_message("/oscVideo/status",
                                   (True, "Started Recording"))
            else:
                self._send_message("/oscVideo/status",
                                   (False, "Couldn't start recording"))
        else:
            self._video_manager.stop_recording()
            self._send_message("/oscVideo/status",
                               (True, "Stopped Recording"))

    def listen(self):
        """
        Initialize the server, start listening.
        """
        dispatcher = Dispatcher()
        try:
            self.server = ThreadingOSCUDPServer((self._address, self._port),
                                                dispatcher)
        except OSError as e:
            self._logger.error(f"Can't start OSC interface: {e}")
            return False

        self._logger.info(
                f"OSC Server listening on {self._address}:{self._port}")
        self.client = SimpleUDPClient(self._remote_address, self._remote_port)

        dispatcher.map("/oscVideo/prepareRecording",
                       self._prepare_recording)
        dispatcher.map("/oscVideo/record", self._record)
        return True

    def run(self):
        self.server.serve_forever()
