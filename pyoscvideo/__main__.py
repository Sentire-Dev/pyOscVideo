

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

import sys
import signal
import logging

from PyQt5.QtWidgets import QApplication

# Initialize logging module
from pyoscvideo.helpers.helpers import setup_logging
from pyoscvideo.helpers.settings import load_settings


class App(QApplication):
    """The application class for initializing the app."""

    def __init__(self, sys_argv):
        """
        Init the QApplication.
        """
        super(App, self).__init__(sys_argv)

        # Setup logging mechanism
        setup_logging()

        self._logger = logging.getLogger(__name__+".App")

        # TODO: this should be a command line option also
        self.settings = load_settings("settings/pyoscvideo.yml")

        self.video_manager = None
        self.osc_interface = None
        self.main_view = None

    def setup(self):
        """
        Setup the app.
        """
        # Only load main modules after settings have been successfuly loaded
        from pyoscvideo.video.camera_selector import CameraSelector
        from pyoscvideo.video.manager import VideoManager
        from pyoscvideo.gui.main_view import MainView
        from pyoscvideo.osc.interface import OSCInterface

        camera_selector = CameraSelector(self.settings.get('camera', {}))
        self.video_manager = VideoManager(camera_selector)

        self.osc_interface = OSCInterface(
                self.video_manager, **self.settings['osc'])
        if not self.osc_interface.listen():
            # Exit if can't start OSC interface
            self._logger.error("Can't start OSC interface, quitting.")
            return False

        # Starr OSC thread
        self.osc_interface.start()

        if self.settings.get('gui', None) is not None:
            # Should load gui
            self.main_view = MainView(self.video_manager,
                                      **self.settings['gui'])
            self.main_view.show()
        else:
            # no gui, main loop is handled by the OSCInterface thread
            # so we need to listen to ctrl+c to stop the OSC thread
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            self.osc_interface.wait()
        return True


def main():
    """Start the application."""
    app = App(sys.argv)
    if app.setup():
        app.exit(app.exec_())


if __name__ == '__main__':
    main()
