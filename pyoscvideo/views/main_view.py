"""
Main View
TODO: add proper description
"""
import time
import queue
import logging
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QImage
from pyoscvideo.views.main_view_ui import Ui_MainWindow

class MainView(QMainWindow):
    """ The main Window
    """
    start_capturing = pyqtSignal()
    should_quit = pyqtSignal()

    def __init__(self, frame_rate):
        super().__init__()
        self._logger = logging.getLogger(__name__+".MainView")
        
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        self._ui.closeEvent = self.closeEvent 
        self._frame_rate = frame_rate
        self.setStatusBar(self._ui.statusbar)

    @pyqtSlot(str)
    def set_status_msg(self, msg):
        self._ui.statusbar.setEnabled(True)
        self._logger.debug("Status changed: %s", msg)
        self._ui.statusbar.showMessage(msg)

    @pyqtSlot(QImage)
    def on_new_frame(self, image):
        """set the image in the main windows
        """
        self._logger.debug("New frame")
        # TODO: scaled should not be called here as it is very expensive
        self._ui.imageLabel.setPixmap(QPixmap.fromImage(image).scaled(
            self._ui.imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        #time_elapsed = time.time() - self._model.last_update
        #self._model.last_update = time.time()
        #print("Time elapsed: " + str(time_elapsed))
        #frame_rate = 1 / time_elapsed
        #print("Fps: " + str(frame_rate))

    @pyqtSlot()
    def on_capture_button_clicked(self):
        self.start_capturing()

    # def resizeEvent(self, event): 
    #     print("resized")
    #     size = self._ui.imageLabel.size()
    #     img = self._ui.imageLabel.pixmap()
    #     if img:
    #         self._ui.imageLabel.setPixmap(img.scaled(
    #             self._ui.imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    @pyqtSlot(float)
    def update_fps_label(self, fps):
        self._ui.frame_rate_label.setText("Fps: " + str(round(fps, 1)))

    def button_clicked(self):
        """ callback function for button click
        """
        print('Button Clicked')
        self.start_capturing()



    def closeEvent(self, event):
        print("event")
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.on_quit()
            event.accept()
        else:
            event.ignore()

    def on_quit(self):
        self.should_quit.emit






