

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
import argparse

from PyQt5.QtWidgets import QApplication, QMessageBox

# Initialize logging module
from pyoscvideo.helpers.helpers import setup_logging
from pyoscvideo.helpers.settings import load_settings


class App(QApplication):
    """The application class for initializing the app."""

    def __init__(self, settings_file, qt_argv):
        """
        Init the QApplication.
        """
        super().__init__(qt_argv)

        # Setup logging mechanism
        setup_logging()

        self._logger = logging.getLogger(__name__+".App")

        # TODO: this should be a command line option also
        self.settings = load_settings(settings_file)

        self.video_manager = None
        self.osc_interface = None
        self.main_view = None

    def setup(self):
        """
        Setup the app.
        """
        # Only load main modules after settings have been successfuly loaded
        from pyoscvideo.video.manager import VideoManager
        from pyoscvideo.gui.main_view import MainView
        from pyoscvideo.osc.interface import OSCInterface

        self.video_manager = VideoManager(self.settings.get('camera', {}))

        self.osc_interface = OSCInterface(
                self.video_manager, **self.settings['osc'])

        gui = self.settings.get('gui', None)

        if not self.osc_interface.listen():
            # Exit if can't start OSC interface
            self._logger.error("Can't start OSC interface, quitting.")
            if gui:
                error_message = QMessageBox()
                error_message.setIcon(QMessageBox.Critical)
                error_message.setText("Can't start OSC interface")
                error_message.setInformativeText(
                        "Could not start OSC interface, check the port is "
                        "available or if pyoscrouter is already running.")
                error_message.setWindowTitle("pyOscVideo")
                error_message.exec_()
            return False

        # Start OSC thread
        self.osc_interface.start()

        if gui is not None:
            # Should load gui
            self.main_view = MainView(self.video_manager,
                                      **gui)
            self.main_view.show()
        else:
            # no gui, main loop is handled by the OSCInterface thread
            # so we need to listen to ctrl+c to stop the OSC thread
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            self.osc_interface.wait()
        return True


def main():
    """Start the application."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--settings', default="settings/pyoscvideo.yml",
                        help="Path to settings file")
    parsed_args, unparsed_args = parser.parse_known_args()
    app = App(parsed_args.settings, unparsed_args)
    if app.setup():
        app.exit(app.exec_())


if __name__ == '__main__':
    main()
