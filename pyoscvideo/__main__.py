"""Entry point of the osc_video application.

TODO: add file description
"""


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

from PyQt5.QtWidgets import QApplication

from pyoscvideo.controllers.main_ctrl import MainController
from pyoscvideo.models import Recorder
from pyoscvideo.gui.main_view import MainView
from pyoscvideo.osc.interface import OSCInterface


class App(QApplication):
    """The application class for initializing the app."""

    def __init__(self, sys_argv):
        """Init the QApplication."""
        super(App, self).__init__(sys_argv)
        self.model = Recorder()
        self.main_controller = MainController(self.model)
        self.main_view = MainView(self.main_controller)
        self.osc_interface = OSCInterface(self.main_controller)
        self.osc_interface.start()

        self.main_view.show()


def main():
    """Start the application."""
    app = App(sys.argv)
    app.exit(app.exec_())


if __name__ == '__main__':
    main()
