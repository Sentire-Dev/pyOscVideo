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
from pyoscvideo.model.camera_selection_model import CameraSelectionModel

# TODO: Global variables should not be defined here
#       instead use Settings Class
# FOURCC = -1 # Should output available codecs, not working at the moment
FOURCC = "MJPG"  # The default codec, works on arch and mac together with .avi extensions
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

    def __init__(self, model, view):
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
        self._main_view = view
        self._recording = False
        self._capturing = False
        # self._main_view._ui.camera_selection_comboBox.currentIndexChanged.connect()
        self._main_view._ui.recordButton.clicked.connect(self.toggle_recording)
        self._main_view.should_quit.connect(self.cleanup)
        self._model.status_msg_changed.connect(self._main_view.set_status_msg)
        self._image_update_thread = None
        self._source = None
        # self._camera_reader = None
        self.read_queue = queue.LifoQueue()
        self._write_queue = queue.LifoQueue()
        self._init_reader()

        self._camera_selector_model = CameraSelectionModel()
        self._camera_selector = CameraSelector(self._camera_selector_model,
                                               self._main_view._ui.camera_selection_comboBox)
        self._camera_selector.selection_changed.connect(self._camera_reader.set_camera)
        self._camera_selector.selection_changed.connect(self.on_camera_selection_changed)
        self._fps_update_thread = None
        self._start_fps_update_thread()
        self._writer = None
        self._init_writer()
        self.frame_rate = 0
        self._camera_reader.set_camera(self._camera_selector.selected_camera)
        self.start_capturing()

    @property
    def read_queue(self):
        """Get the queue for reading frames."""
        return self.__read_queue

    @read_queue.setter
    def read_queue(self, read_queue):
        """Get the queue for reading frames."""
        # TODO type check
        self.__read_queue = read_queue

    def on_camera_selection_changed(self):
        """Callback for camera selection change."""
        self._logger.info('Changed')
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
        self._writer = VideoWriter(self._write_queue, FOURCC, FPS, self._camera_reader.size)

    def start_capturing(self):
        """Start capturing frames from the defined source.
        
        Creates CameraReader Object and sets the source and the state
        TODO: add return value which indicates if capturing actually started
        """
        self._logger.info("Start capturing")

        if self._model.is_capturing:
            self._logger.warning("Already Capturing")
            self.set_status_msg("Could not start capturing")
            return False

        if self._camera_reader.ready:
            self._start_image_update_thread()
            self._capturing = True
            return True
        self._logger.warning("Could not start capturing")

        # if self._camera_reader.set_camera(self._camera_selector.selected_camera):
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
        self._fps_update_thread.updateFpsLabel.connect(self._main_view.update_fps_label)
        self._fps_update_thread.start()

    def prepare_recording(self, filename):
        """Prepare the recording.
        
        If not capturing yet, starts the capturing, and tries to create a file
        with the set file extension.
        
        TODO: provide return value which indicates if preparation was successful
        """
        filename = filename + ".avi"
        self._logger.info("Preparing recording: %s", filename)
        if not self._capturing:
            self.start_capturing()

        # check if camera is available

        if self._camera_reader.ready:
            assert isinstance(filename, str)
            self._writer.size = self._camera_reader.size
            self._writer.prepare_writing(filename)
            self._camera_reader.add_queue(self._write_queue)
        # if not try to start capturing
        else:
            print("Camera Reader not initialized")
        if self._writer:
            pass
            # liblo.send(self.target, "/oscVideo/status", True, "Prepared Recording")
        else:
            print("Video writer not initialized")
            # liblo.send(self.target, "/oscVideo/status", False, "Could not prepare Recording")

    def toggle_recording(self):
        """Toggle the Recording.

        If not recording make a new recording with time stamped filename. Otherwise stop the current recording.
        """
        self._logger.info("Toggle Recording")
        if not self._recording:
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
        if not self._recording:
            self.prepare_recording(filename)
            if self._writer.ready:
                self.start_recording()
            else:
                msg = "Could not start Recording. Check filename"
                self._logger.warning(msg)
                # liblo.send(self.target, "/oscVideo/status", False,
                #           msg)
        else:
            self.stop_recording()
            self.new_recording(filename)

    def start_recording(self):
        """Start the recording.


        """

        if self._camera_reader.ready and self._writer.ready:
            self._writer.start_writing()
            self._recording = True
            msg = "Started Recording"
            self._logger.info(msg)
            # liblo.send(self.target, "/oscVideo/status", True, msg)
        else:
            msg = "Could not start recording, camera reader or writer not ready"
            # liblo.send(self.target, "/oscVideo/status", False, msg)
            self._recording = False
            self._logger.warning(msg)

    def stop_recording(self):
        """Stop the recording and print out statistics.

        TODO: add return values
        """
        if self._recording:
            self._recording = False
            frames_written, recording_time = self._writer.stop_writing()
            self._camera_reader.remove_queue(self._write_queue)
            self._logger.info("Stopped Recording")
            self._logger.info("Recording Time: %.1fs", recording_time)
            self._logger.info("%i frames written", frames_written)
            if recording_time > 0:
                self._logger.info("Average frame rate: %.2f", + (frames_written / recording_time))
            # liblo.send(self.target, "/oscVideo/status", True, "Stopped Recording")
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
        self._image_update_thread = UpdateImage(self.read_queue, self._model.frame_rate)
        self._image_update_thread.change_pixmap.connect(self._main_view.on_new_frame)
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

        cv_image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], qt_format)
        cv_image = cv_image.rgbSwapped()
        return cv_image


# class OscVideo():
#     """ Class for recording and playing video files via OSC commands """
#     def __init__(self):
#         # Define the codec and create VideoWriter object
#         print("Init OSC Video")
#         self.writer = None
#         self.video_reader = None
#         self.camera_reader = None
#         self.queue = queue.Queue()
#         self.recording = False
#         self.playing = False
#         self.source = Sources.NotSpecified
#         self.send_target = None
#         self.capturing = False

#         try:
#             self.target = liblo.Address(TARGET_HOSTNAME, TARGET_PORT)
#         except liblo.AddressError as err:
#             print(str(err))
#             sys.exit()

#     def prepare_playing(self, filename):
#         """Prepare playback of video file.

#         Checks if video with the given filename and with any of the supported
#         file extensions exists in the given set folder path and opens it for
#         reading.

#         Arguments:
#             filename {String} -- the filename of the video without extension

#         Returns:
#             success {Boolean} -- if preparing the video playback was successful
#         """
#         fullname = self.check_if_file_exists(filename)
#         if not fullname:
#             print("File " + filename + " does not exist")
#             return False

#         #filename += extension
#         if not self.playing:
#             self.video_reader = VideoReader()
#             if self.video_reader.open_file(fullname):
#                 liblo.send(self.target, "/oscVideo/status", True, "Prepared Playing")
#                 return True
#         print("Cannot prepare playing, already playing")
#         liblo.send(self.target, "/oscVideo/status", False, "Already Playing")
#         return False


#     def check_if_file_exists(self, filename):
#         """Check if the file exists

#         Checks if a video file with the given filename and any of the supported
#         extensions exists in the configured folder path

#         Args:
#             filename: the filename without extensions

#         Returns:
#             Filename with extensions if file exists or False if no video file
#             found
#         """
#         fullname = None
#         for ext in SupportedFileFormats.All:
#             fullname = os.getcwd() + "/" + filename + ext
#             print(fullname)
#             if os.path.isfile(fullname):
#                 return fullname
#             print("No file found with name: " + filename)
#             liblo.send(self.target, "/oscVideo/status", False, "File not found")
#             return False


#     def start_playing(self):
#         """Starts playback.
#         TODO: add return value
#         """
#         if not self.playing:
#             if not self.recording:
#                 if self.video_reader.start_playing(): # TODO: rename to is_ready
#                     self.source = Sources.Video
#                 self.playing = True
#                 liblo.send(self.target, "/oscVideo/status", True, "Started Playing")
#             else:
#                 print("In recording mode. Won't start playing")
#                 liblo.send(self.target, "/oscVideo/status", False, "In recording Mode")
#         else:
#             print("Already Playing")
#             liblo.send(self.target, "/oscVideo/status", False, "Already Playing")


#     def stop_playing(self):
#         """Stops playback."""
#         if self.source == Sources.Video:
#             self.source = Sources.NotSpecified
#             self.playing = False
#             print("Stopped Playing")
#             liblo.send(self.target, "/oscVideo/status", True, "Stopped Playing")
#         else:
#             print("Not playing. Nothing to stop")
#             liblo.send(self.target, "/oscVideo/status", False, "Not Playing")

#     def stop_capturing(self):
#         """Stop capturing."""
#         self.source = Sources.NotSpecified
#         self.camera_reader.release()
#         liblo.send(self.target, "/oscVideo/status", True, "Stopped Capturing")
#         self.capturing = False


#     def release(self):
#         """releases all created Objects."""
#         if self.video_reader:
#             self.video_reader.release()

#         if self.camera_reader:
#             self.camera_reader.release()

#         if self.writer:
#             self.writer.release()
#         #cv2.destroyAllWindows()

#     def print_user_input_message(self):
#         """Prints user instructions to terminal."""
#         print("Waiting for user input")
#         print(" c: start and stop capturing")
#         print(" r: start and stop recording")
#         print(" q: quit")
#         print("Press key...")

#     @staticmethod
#     def create_blank_img(width, height, rgb_color=(0, 0, 0)):
#         """Create new image (numpy array) filled with given color in RGB.

#         Returns:
#             image (array) in numpy format
#         """
#         # Create black blank image
#         image = np.zeros((height, width, 3), np.uint8)
#         # Since OpenCV uses BGR, convert the color first
#         color = tuple(reversed(rgb_color))
#         # Fill image with color
#         image[:] = color
#         return image


# class Sources(object):
#     ''' Defines available image Sources
#     '''

#     Video = "Video"
#     Camera = "Camera"
#     NotSpecified = "None"
#     All = (Video, Camera, NotSpecified)

# class SupportedFileFormats(object):
#     ''' Defines the supported file formats

#     The supported file formats

#     TODO: should be platform specific
#     TODO: Add more File formats
#     '''
#     Avi = ".avi" # workks on arch and win
#     Mpeg4 = ".mpeg4"
#     All = (Avi, Mpeg4)

# class OscServer(liblo.ServerThread):
#     """ Provides OSC Interface

#     Inherits from liblo.ServerThread

#     Defines callback functions for OSC messages
#     """
#     def __init__(self, writer):
#         self.osc_video = writer # TODO: should not own writer/osc_video instance
#         liblo.ServerThread.__init__(self, LISTEN_PORT)

#     @liblo.make_method('/oscVideo/newRecording', 's')
#     def new_record(self, path, args):
#         """Callback Function for for starting a new recording."""
#         filename = args[0]
#         print("Received message '%s' with argument: %s" % (path, filename))
#         self.osc_video.new_recording(filename)

#     @liblo.make_method('/oscVideo/prepareRecording', 's')
#     def prepare_recording(self, path, args):
#         """Callback Function for preparing a recording.

#         Calling start_recording() immediately after Camera is opened results in "OpenCV: AVF:
#         waiting to write video data." messages and Blocks the server.

#         prepareRecording opens the Camera first and starts Capturing so that recording can start
#         without blocking the Program execution.

#         TODO: Find the cause for the message and implement testing if recording is ready.
#         """
#         filename = args[0]
#         print("Received message '%s' with arguments: %s" % (path, args))
#         self.osc_video.prepare_recording(filename)


#     @liblo.make_method('/oscVideo/preparePlaying', 's')
#     def prepare_playing(self, path, args):
#         """Callback function for Video Playback Preparation"""
#         filename = args[0]
#         print("Received message '%s' with argument '%s'" % (path, filename))
#         self.osc_video.prepare_playing(filename)

#     @liblo.make_method('/oscVideo/play', 'i')
#     def play(self, path, args):
#         """Callback function for Video Playback"""
#         play = args[0]
#         if play == 1:
#             self.osc_video.start_playing()
#         elif play == 0:
#             self.osc_video.stop_playing()


#     @liblo.make_method('/oscVideo/record', 'i')
#     def record(self, path, args):
#         """Callback function for video recording"""
#         record = args[0]
#         if record == 1:
#             self.osc_video.start_recording()
#         elif record == 0:
#             self.osc_video.stop_recording()


#     @liblo.make_method('/oscVideo/stopRecording', None)
#     def stop_recording(self, path, args):
#         """Callback Function for for stop the recording."""
#         print("Received message '%s'" % path)
#         self.osc_video.stop_recording()


#     @liblo.make_method(None, None)
#     def fallback(self, path, args):
#         """Generic handler for unknown messages."""
#         print("Received unknown message '%s' with arguments '%s'" % (path, args))


# class VideoReader():
#     """ Captures Video from File
#     """
#     def __init__(self):
#         self.capture = None
#         self.filename = None
#         self.first_frame_time = None
#         self.last_frame_time = None
#         self.frames_read = 0
#         self.fps = None
#         self.frame_duration = None

#     def open_file(self, filename):
#         """ opens the file

#         Parameters
#         ----------

#         filename: the full path to the file with extension
#         """
#         self.filename = filename
#         self.capture = cv2.VideoCapture(filename)

#         if self.capture.isOpened():
#             self.fps = self.capture.get(cv2.CAP_PROP_FPS)
#             self.frame_duration = 1/self.fps
#             print("Succuessfully opened file: " + filename)
#             return True
#         print("Error opening video file: " + filename)
#         return False

#     def start_playing(self):
#         """ starts the playback of the video file """
#         print("Started Playing Video")

#         if self.capture.isOpened():
#             return True
#             # moved to main thread

#             # # Capture frame-by-frame
#             # success, frame = self.capture.read()
#             # if success:
#             #     # Display the resulting frame
#             #     cv2.imshow(window_name, frame)
#             #     # Press Q on keyboard to  exit
#             #     if cv2.waitKey(30) & 0xFF == ord('q'):
#             #         break
#             # # Break the loop
#             # else:
#             #     print("Could not grab frame, stop playing now")
#             #     self.playing = False
#             #     break
#         else:
#             print("No file ready to play")
#             return False
#         #self.release()

#     def stop_playing(self):
#         """ stops the playback of the video file """
#         self.release()

#     def read(self):
#         """ reads one frame from the source

#         Returns
#         -------

#         success (boolean): true if frame could be read,
#         frame (array): the image frame in cv format,
#         sleep_time (float): the time in seconds the program should sleep in
#         order to guarantee constant frame rate
#         """
#         success, frame = self.capture.read()
#         if not success:
#             print("Could not read frame")
#             self.stop_playing()
#             return (False, None, None)
#         if frame is not None:
#             if self.frames_read == 0:
#                 self.first_frame_time = time.time()
#             self.frames_read += 1
#             self.last_frame_time = time.time()
#         if self.first_frame_time is None:
#             sleep_time = self.frame_duration
#         else:
#             calculated_time = self.first_frame_time + self.frames_read*self.frame_duration
#             sleep_time = max(0, calculated_time - time.time())
#         return (True, frame, sleep_time)

#     def release(self):
#         """ releases the capture """
#         self.capture.release()
#         cv2.destroyAllWindows()


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
