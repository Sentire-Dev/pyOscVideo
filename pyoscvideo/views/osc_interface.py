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

    def _prepare_recording(self, addr, filename):
        print(filename)
        if self._controller.prepare_recording(filename):
            self.client.send_message("/oscVideo/status", (True, "Prepared Recording"))
        else:
            self.client.send_message("/oscVideo/status", (False, "Could not prepare Recording"))

    def _record(self, addr, record):
        if record:
            if self._controller.start_recording():
                self.client.send_message("/oscVideo/status", (True, "Started Recording"))
            else:
                self.client.send_message("/oscVideo/status", (False, "Couldn't start recording"))
        else:
            self._controller.stop_recording()

    def _stop_recording(self, *args):
        print(args)

    def run(self):
        self._logger.info("Running OSC thread")
        self._should_run = True
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
 
        self._dispatcher = Dispatcher()
        self.server = AsyncIOOSCUDPServer((self._address, self._port), self._dispatcher, self._loop)
        self.client = SimpleUDPClient("127.0.0.1", 57120)

        self._dispatcher.map("/oscVideo/prepareRecording", self._prepare_recording)
        self._dispatcher.map("/oscVideo/record", self._record)
        self._dispatcher.map("/oscVideo/stopRecording", self._stop_recording)

        self._logger.info(f"OSC Server is listening on {self._address}:{self._port}")

        self.server.serve()
        self._loop.run_forever()
        
        self._logger.info(f"OSC Server finished")
