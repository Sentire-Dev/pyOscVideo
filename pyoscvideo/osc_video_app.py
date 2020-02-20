"""Entry point of the osc_video application.

TODO:
    - add Version number
    - add author
    - add license
"""
import sys
from PyQt5.QtWidgets import QApplication
from pyoscvideo.model.model import Model
from pyoscvideo.controllers.main_ctrl import MainController
from pyoscvideo.views.main_view import MainView


class App(QApplication):
    """The application class for initializing the app."""

    def __init__(self, sys_argv):
        """Init the QApplication."""
        super(App, self).__init__(sys_argv)
        self.model = Model()
        self.main_view = MainView(self.model.frame_rate)
        self.main_controller = MainController(self.model, self.main_view)

        self.main_view.show()


def main():
    """Start the application."""
    app = App(sys.argv)
    app.exit(app.exec_())


if __name__ == '__main__':
    main()
