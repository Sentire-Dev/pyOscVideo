# pylint: disable=trailing-whitespace
"""Source Code for the MainController Class of the pyoscvideo module.

TODO:
    - add Version number
    - add author
    - add license
"""
import logging
import queue
import time

# import liblo
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtGui import QImage
from cv2.cv2 import VideoWriter_fourcc

from pyoscvideo.controllers.camera_reader import CameraReader
from pyoscvideo.controllers.camera_selector import CameraSelector
from pyoscvideo.controllers.video_writer import VideoWriter
from pyoscvideo.helpers import helpers
from pyoscvideo.model.model import CameraSelectorModel

# TODO: Global variables should not be defined here
#       instead use Settings Class
# FOURCC = -1 # Should output available codecs, not working at the moment

# The default codec, works on arch and mac together with .avi extensions
FOURCC = "MJPG"
# FOURCC = "xvid" # The default codec
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080
PLAY_FILENAME = "output"
LISTEN_PORT = 1234
FPS = 30
TARGET_PORT = 57120
TARGET_HOSTNAME = "localhost"
WINDOW_NAME = "OSCVideo"


def _generate_filename():
    time_str = time.strftime("%Y%m%d_%H%M%S")
    filename = "OSCVideo_Recording_" + time_str
    return filename


class MainController(QObject):
    """The main controller object.

    TODO: add logger
    """
    _camera_reader: CameraReader

    def __init__(self, model):
        """Init the main controller.

        Arguments:
            model {QObject} -- [The model]

        Raises:
            InitError: If CameraReader could not be initialized correctly
        """
        super().__init__()
        helpers.setup_logging()
        self._logger = logging.getLogger(__name__ + ".MainController")
        self._logger.info("Initializing")
        self._model = model
        self._image_update_thread = None
        self._source = None
        self._camera_reader = None
        self.read_queue = queue.LifoQueue()
        self._write_queue = queue.LifoQueue()
        self._init_reader()

        self._camera_selector = CameraSelector(CameraSelectorModel())
        self._camera_selector._model.selection_changed.connect(
                self.on_camera_selection_changed)
        self._fps_update_thread = None
        self._start_fps_update_thread()
        self._writer = None
        self._init_writer()
        self.frame_rate = 0

    @property
    def read_queue(self):
        """Get the queue for reading frames."""
        return self.__read_queue

    @read_queue.setter
    def read_queue(self, read_queue):
        """Get the queue for reading frames."""
        # TODO type check
        self.__read_queue = read_queue

    def on_camera_selection_changed(self, device_id):
        """Callback for camera selection change."""
        self._logger.info(f"Changed camera selection to device: {device_id}")
        self._camera_reader.set_camera(device_id)
        self.start_capturing()

    def _init_reader(self):
        try:
            fourcc = VideoWriter_fourcc('M', 'J', 'P', 'G')
            # TODO: Automatically select highest resolution
            options = {"CAP_PROP_FOURCC": fourcc,
                       "CAP_PROP_FRAME_WIDTH": CAMERA_WIDTH,
                       "CAP_PROP_FRAME_HEIGHT": CAMERA_HEIGHT
                       }
            self._camera_reader = CameraReader(self.read_queue, options)
        except Exception as err:
            print(str(err))
            raise InitError("OscVideo()", "Could not initialise CameraReader")

    def _init_writer(self):
        self._writer = VideoWriter(self._write_queue,
                                   FOURCC,
                                   FPS,
                                   self._camera_reader.size)

    def start_capturing(self):
        """Start capturing frames from the defined source.

        Creates CameraReader Object and sets the source and the state
        TODO: add return value which indicates if capturing actually started
        """
        self._logger.info("Start capturing")

        if self._model.is_capturing:
            self._logger.warning("Already Capturing")
            self._model._status_msg = "Could not start capturing"
            return False

        if self._camera_reader.ready:
            self._start_image_update_thread()
            self._model.is_capturing = True
            return True
        self._logger.warning("Could not start capturing")

        # if self._camera_reader.set_camera(
        #       self._camera_selector.selected_camera):
        #     #self.source = Sources.Camera
        #     msg = "Started Capturing"
        #     self._main_view.set_status_msg(msg)
        #     #liblo.send(self.target, "/oscVideo/status", True, msg)
        #     #self.capturing = True
        #     self.frame_rate = self._camera_reader.frame_rate
        #     #time.sleep(0.5)
        #     self._camera_reader.start_buffering()
        #     self._model.capturing = True
        #     self._start_image_update_thread()
        #     return True
        # msg = "Could not open camera"
        # self._logger.warning(msg)
        # self._main_view.set_status_msg(msg)
        # liblo.send(self.target, "/oscVideo/status", False, msg)
        return False

    def _start_fps_update_thread(self):
        """Spawn the fps update thread."""
        self._fps_update_thread = UpdateFps(self._model)
        # self._fps_update_thread.updateFpsLabel.connect(self._main_view.update_fps_label)
        self._fps_update_thread.start()

    def prepare_recording(self, filename):
        """Prepare the recording.

        If not capturing yet, starts the capturing, and tries to create a file
        with the set file extension.

        TODO: provide return value indicating if preparation was successful
        """
        filename = filename + ".avi"
        self._logger.info("Preparing recording: %s", filename)
        if not self._model.is_capturing:
            self.start_capturing()

        # check if camera is available
        if self._camera_reader.ready:
            assert isinstance(filename, str)
            self._writer.size = self._camera_reader.size
            if not self._writer.prepare_writing(filename):
                return False
            self._camera_reader.add_queue(self._write_queue)
        # if not try to start capturing
        else:
            print("Camera Reader not initialized")

        if self._writer:
            return True

        print("Video writer not initialized")
        return False

    def toggle_recording(self):
        """Toggle the Recording.

        If not recording make a new recording with time stamped filename.
        Otherwise stop the current recording.
        """
        self._logger.info("Toggle Recording")
        if not self._model.is_recording:
            filename = _generate_filename()
            self.new_recording(filename)
        else:
            self.stop_recording()

    def new_recording(self, filename):
        """Start a new recording.

        Stops the current recording, prepares a new one and starts it.

        Arguments:
            filename {String} -- the filename of the recording

        Note:
            Should only be called if instantaneous recording is not needed
            since it takes some time to prepare the recording.

        See Also:
            prepare_recording()
        """
        if not self._model.is_recording:
            self.prepare_recording(filename)
            if self._writer.ready:
                self.start_recording()
            else:
                self._logger.warning(
                        "Could not start Recording. Check filename")
        else:
            self.stop_recording()
            self.new_recording(filename)

    def start_recording(self):
        """Start the recording.
        """

        if self._camera_reader.ready and self._writer.ready:
            self._writer.start_writing()
            self._model.is_recording = True
            msg = "Started Recording"
            self._logger.info(msg)
            return True

        self._model.is_recording = False
        self._logger.warning(
            "Could not start recording, camera reader or writer not ready")
        return False

    def stop_recording(self):
        """Stop the recording and print out statistics.

        TODO: add return values
        """
        if self._model.is_recording:
            self._model.is_recording = False
            frames_written, recording_time = self._writer.stop_writing()
            self._camera_reader.remove_queue(self._write_queue)
            self._logger.info("Stopped Recording")
            self._logger.info("Recording Time: %.1fs", recording_time)
            self._logger.info("%i frames written", frames_written)
            if recording_time > 0:
                avg = frames_written / recording_time
                self._logger.info(f"Average frame rate: {avg:.2f}")
            # Re-init the writer
            # TODO: review this because it doesn't seem correct to re-init
            # it here
            self._writer = None
            self._init_writer()
        else:
            self._logger.warning("Not recording")

    def on_new_frame(self):
        """set the image in the main windows
        """
        self._model.frame_counter += 1

    def _start_image_update_thread(self):
        """Start the capturing of frames.

        Spawns the image update thread.
        """
        if self._image_update_thread:
            self._image_update_thread.quit()

        self._image_update_thread = UpdateImage(
                self.read_queue, self._model.frame_rate)
        self._image_update_thread.new_frame.connect(self.on_new_frame)

        self._image_update_thread.start()

    # def get_frame(self):
    #     # get most recent frame
    #     # while not self._frame_queue.empty():
    #     frame = None
    #     if self._camera_reader:
    #         frame = self._camera_reader.stream.read()

    #     if frame is not None:
    #         image = self.cv2qt(frame)
    #         #print('converting frame')
    #         return image
    #     #print("Queue empty")
    #     return None

    def cleanup(self):
        """Perform necessary action to guarantee a clean exit of the app."""
        self._camera_reader.release()
        self._fps_update_thread.quit()
        if self._image_update_thread:
            self._image_update_thread.quit()


class UpdateFps(QThread):
    """Calculate current framerate every second and update the Fps label."""

    updateFpsLabel = pyqtSignal(float)

    def __init__(self, model):
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".UpdateFps")
        self._model = model
        self._time_last_update = time.time()
        self._update_interval = 1

    def run(self):
        """Run the Thread worker."""
        self._logger.info("Started fps label update thread")
        while True:
            time_now = time.time()
            time_passed = time_now - self._time_last_update
            frame_rate = float(self._model.frame_counter / time_passed)
            self._model.frame_counter = 0
            self.updateFpsLabel.emit(frame_rate)
            self._time_last_update = time.time()
            time.sleep(1)


class UpdateImage(QThread):
    """ Thread for reading frames from the source and updating the image
    """
    new_frame = pyqtSignal()
    change_pixmap = pyqtSignal(QImage)

    def __init__(self, frame_queue, frame_rate):
        """Init the UpdateImage Thread."""
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".UpdateImage")
        self._queue = frame_queue

        if frame_rate == 0:
            self._logger.error("Frame rate cannot be 0")
            raise RuntimeError
        self._frame_duration = 1 / frame_rate
        self._time_last_update = time.time()

    def run(self):
        """Run the worker."""
        self._logger.info("Started image update thread")

        forward_frames = 0
        while True:
            while not self._queue.empty():
                try:
                    frame = self._queue.get_nowait()
                    self._logger.debug("emit image")
                    image = self.cv2qt(frame)
                    self.change_pixmap.emit(image)
                    self.new_frame.emit()
                    self._time_last_update = time.time()
                except queue.Empty:
                    # exception raised sometimes anyway
                    # check again:
                    if self._queue.empty():
                        self._logger.debug("queue is empty")
                        self._logger.debug("fast forward frame")
                        forward_frames += 1
            delta_time = time.time() - self._time_last_update
            self._logger.debug("Queue is empty")
            if delta_time < self._frame_duration:
                sleep = self._frame_duration - delta_time
                self._logger.debug("Waiting %s seconds", sleep)
                time.sleep(sleep)

    @staticmethod
    def cv2qt(frame):
        """Convert an image frame from cv to qt format.

        Arguments:
            frame {[type]} -- [description]

        Returns:
            [type] -- [description]
        """
        qt_format = QImage.Format_Indexed8
        if len(frame.shape) == 3:
            if frame.shape[2] == 4:
                qt_format = QImage.Format_RGBA8888
            else:
                qt_format = QImage.Format_RGB888

        cv_image = QImage(frame, frame.shape[1], frame.shape[0],
                          frame.strides[0], qt_format)
        cv_image = cv_image.rgbSwapped()
        return cv_image


class Error(Exception):
    """Base class for exceptions in this module."""


class InitError(Error):
    """Exception raised for errors at intialising.

    Args:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        """Init the Error."""
        super().__init__(message)
        self.expression = expression
        self.message = message
