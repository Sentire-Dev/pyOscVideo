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


from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.dispatcher import Dispatcher

from PyQt5.QtCore import QThread

import asyncio
import logging


def filter_handler(address, *args):
    print(f"{address}: {args}")


class OSCInterface(QThread):
    def __init__(self, controller, address="0.0.0.0", port=57220):
        super().__init__()
        self._logger = logging.getLogger(__name__+".OSCInterface")
        self._logger.info("Initializing OSC thread")
        self._dispatcher = None
        self._controller = controller
        self._address = address
        self._port = port
        self._loop = None
        self._should_run = False

        self.server = None
        self.client = None

    def _send_message(self, path, args):
        self._logger.info(
                f"Sending message '{path}' with args '{args}' to client")
        self.client.send_message(path, args)

    def _prepare_recording(self, addr, filename=None):
        self._logger.info(
                f"Prepare recording with filename: {filename}")
        if not filename:
            self._logger.warning("No filename argument")
        elif self._controller.prepare_recording(filename):
            self._send_message("/oscVideo/status",
                               (True, "Prepared Recording"))
        else:
            self._send_message("/oscVideo/status",
                               (False, "Could not prepare Recording"))

    def _record(self, addr, record=None):
        if record is None:
            self._logger.warning(f"No argument sent, expecting "
                                 f"a boolean to start or stop recording")
        elif record:
            if self._controller.start_recording():
                self._send_message("/oscVideo/status",
                                   (True, "Started Recording"))
            else:
                self._send_message("/oscVideo/status",
                                   (False, "Couldn't start recording"))
        else:
            self._controller.stop_recording()
            self._send_message("/oscVideo/status",
                               (True, "Stopped Recording"))

    def run(self):
        self._logger.info("Running OSC thread")
        self._should_run = True
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        self._dispatcher = Dispatcher()
        self.server = AsyncIOOSCUDPServer((self._address, self._port),
                                          self._dispatcher, self._loop)
        self.client = SimpleUDPClient("127.0.0.1", 57120)

        self._dispatcher.map("/oscVideo/prepareRecording",
                             self._prepare_recording)
        self._dispatcher.map("/oscVideo/record", self._record)

        self.server.serve()
        self._logger.info(
                f"OSC Server listening on {self._address}:{self._port}")
        self._loop.run_forever()

        self._logger.info(f"OSC Server finished")
