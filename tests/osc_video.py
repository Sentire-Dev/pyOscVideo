import sys
import time
import Queue
import os.path
from multiprocessing.pool import ThreadPool
from liblo import ServerThread, make_method, ServerError
import cv2
import numpy as np

FOURCC = "mp4v" # The default codec
FILENAME = "output.mpeg4" # The default filname if nothing is set
LISTEN_PORT = 1234
FPS = 24
DEVICE = 0
WINDOW_NAME = "OSCVideo"

class Sources(object):
    Video = "Video"
    Camera = "Camera"
    NotSpecified = "None"

    All = (Video, Camera, NotSpecified)

class OscServer(ServerThread):
    def __init__(self, writer):
        self.osc_video = writer
        ServerThread.__init__(self, LISTEN_PORT)

    @make_method('/oscVideo/newRecording', 's')
    def new_record(self, path, args):
        """Callback Function for for starting a new recording."""
        filename = args[0]
        print "Received message '%s' with argument: %s" % (path, filename)
        self.osc_video.new_recording(filename)

    @make_method(None, None)
    def fallback(self, path, args):
        """Generic handler for unknown messages."""
        print "received unknown message '%s' witih arguments '%s'" % (path, args)

class CameraReader(object):
    def __init__(self, device_ide, queue):
        self.camera = cv2.VideoCapture(device_ide)
        if not self.camera:
            print "Could not open Camera with ID " + str(device_ide)
        self.queue = queue
        self.buffering = False
        img_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        img_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.size = (img_width, img_height)
        print "Initialized Camera Reader"
        #self.async_result = self.pool.apply_async(self.read_worker)

    # def read_worker(self):
    #     print "Started capturing"
    #     while self.camera.isOpened():
    #         ret, frame = self.camera.read()
    #         if ret:
    #             if self.buffering:
    #                 # write the frame to queue
    #                 self.queue.put(frame)
    #             cv2.imshow('frame', frame)
    #         else:
    #             break
    #     print "Stopped capturing"

    def start_buffering(self):
        self.buffering = True

    def stop_buffering(self):
        self.buffering = False

    def release(self):
        self.camera.release()

class VideoReader(object):
    def __init__(self):
        self.playing = False
        self.capture = None
        self.filename = None

    def open_file(self, filename):
        self.filename = filename
        self.capture = cv2.VideoCapture(filename)
        if self.capture.isOpened():
            print "Succuessfully opened file: " + filename
            return True
        print "Error opening video file: " + filename
        return False

    def start_playing(self):
        self.playing = True
        window_name = "OSCVideo Playback: " + self.filename
        cv2.namedWindow(window_name)
        cv2.moveWindow(window_name, 0, 0)
        print "Started Playing Video"

        while self.capture.isOpened():
            # Capture frame-by-frame
            success, frame = self.capture.read()
            if success:
                # Display the resulting frame
                cv2.imshow(window_name, frame)
                # Press Q on keyboard to  exit
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
            # Break the loop
            else:
                print "Could not grab frame, stop playing now"
                self.playing = False
                break
        else:
            print "No file ready to play"
        self.release()

    def stop_playing(self):
        self.release()

    def release(self):
        self.capture.release()
        cv2.destroyAllWindows()

class VideoWriter(object):
    def __new__(cls, filename, fourcc, fps, size):
        # Check if file exists already
        if not os.path.isfile(filename):
            return super(VideoWriter, cls).__new__(cls, filename, fourcc, fps, size)
        print "File " + filename + " already exists!"
        return None

    def __init__(self, filename, *options):
        self.pool = ThreadPool(processes=1)
        self.filename = filename
        self.options = options
        self.writer = None
        fourcc_id = options[0]
        fourcc = cv2.VideoWriter_fourcc(*fourcc_id)
        self.writer = cv2.VideoWriter(filename, fourcc, self.options[1], self.options[2])
        self._stop = False
        self.async_result = None

    def write_worker(self, queue):
        frame = None
        frames_written = 0
        first_frame_time = None
        last_frame_time = None
        frame_duration = 1./self.options[1]
        while True:
            if self._stop:
                recording_time = last_frame_time - first_frame_time
                return (frames_written, recording_time)
            # get most recent frame
            while not queue.empty():
                frame = queue.get_nowait()
            if frame is not None:
                if frames_written == 0:
                    first_frame_time = time.time()
                if self.writer:
                    self.writer.write(frame)
                    frames_written += 1
                    last_frame_time = time.time()
            if first_frame_time is None:
                sleep_time = frame_duration
            else:
                calculated_time = first_frame_time + frames_written*frame_duration
                sleep_time = max(0, calculated_time - time.time())
            time.sleep(sleep_time)

    def start_writing(self, queue):
        self.async_result = self.pool.apply_async(self.write_worker, (queue,))

    def stop_writing(self):
        self._stop = True
        frames_written, recording_time = self.async_result.get()
        return (frames_written, recording_time)

    def release(self):
        if self.writer:
            self.stop_writing()
            self.writer.release()

class OscVideo(object):
    def __init__(self):
        # Define the codec and create VideoWriter object
        self.writer = None
        self.video_reader = None
        self.camera_reader = None
        self.queue = Queue.Queue()
        self.start_time = None
        self.stop_time = None
        self.recording = False
        self.source = Sources.NotSpecified

    def stat_playing(self):
        self.video_reader = VideoReader()
        self.video_reader.open_file(FILENAME)
        #self.video_reader.start_playing()

    def start_capturing(self):
        self.camera_reader = CameraReader(DEVICE, self.queue)
        self.source = Sources.Camera

    def stop_capturing(self):
        self.source = Sources.NotSpecified
        self.camera_reader.release()

    def new_recording(self, filename):
        # if already recording, stop first and create a new writer
        if not self.recording:
            # check if camera is available
            if self.camera_reader:
                self.writer = VideoWriter(filename, FOURCC, FPS, self.camera_reader.size)
            # if not try to start capturing
            else:
                print "Not Capturing Yet. Will try to open camera now"
                self.start_capturing()
                # try again
                self.writer = VideoWriter(filename, FOURCC, FPS, self.camera_reader.size)
            if self.writer:
                print "Initialized writer"
                self.start_recording()
            else:
                print "Could not init VideoWriter Instance. Check Filename"
        else:
            self.stop_recording()
            self.new_recording(filename)

    def start_recording(self):
        self.camera_reader.start_buffering()
        self.writer.start_writing(self.queue)
        print "Started Recording"
        self.recording = True

    def stop_recording(self):
        if self.recording:
            self.recording = False
            frames_written, recording_time = self.writer.stop_writing()
            self.stop_time = time.time()
            print "Stopped Recording"
            print "Recording Time: " +  str(recording_time) + "s"
            print str(frames_written) + " frames written"
            print "Average frame rate: " + str(frames_written/recording_time) + "fps"
        else:
            print "Not recording, nothing to stop"

    def release(self):
        # Release everything if job is finished
        if self.video_reader:
            self.video_reader.release()

        if self.camera_reader:
            self.camera_reader.release()

        if self.writer:
            self.writer.release()
        cv2.destroyAllWindows()

    def main_loop(self):
        # The below Code should be in CameraReader.read_worker, but due to an bug on Mac OS
        # "Terminating app due to uncaught exception 'NSInternalInconsistencyException',
        # reason: '+[NSUndoManager (NSInternal) _endTopLevelGroupings] is only safe to invoke on
        # the main thread."
        # this needs to run in main thread


        window_name = "OSCVideo"
        cv2.namedWindow(window_name)
        cv2.moveWindow(window_name, 0, 0)

        # Create new blank 600x400 black image
        width, height = 600, 400

        black = (0, 0, 0)
        image = self.create_blank_img(width, height, rgb_color=black)

        print "Waiting for user input"
        while True:
            success = None
            frame = None
            if self.source == Sources.Camera:
                success, frame = self.camera_reader.camera.read()
            elif self.source == Sources.Video:
                success, frame = self.video_reader.capture.read()
            elif self.source == Sources.NotSpecified:
                frame = image
                success = True
            if success:
                if self.recording:
                    # write the frame to queue
                    self.queue.put(frame)
                cv2.imshow(window_name, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('c'):
                    self.start_capturing()
                elif key == ord('q'):
                    break
                elif key == ord('r'):
                    if self.recording:
                        self.stop_recording()
                    else:
                        self.new_recording(FILENAME)
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            else:
                break
        if self.recording:
            self.stop_recording()
        self.release()

    @staticmethod
    def create_blank_img(width, height, rgb_color=(0, 0, 0)):
        """Create new image (numpy array) filled with certain color in RGB"""
        # Create black blank image
        image = np.zeros((height, width, 3), np.uint8)

        # Since OpenCV uses BGR, convert the color first
        color = tuple(reversed(rgb_color))
        # Fill image with color
        image[:] = color

        return image

def main():
    try:
        osc_video = OscVideo()
    except StandardError, err:
        print str(err)
        sys.exit()

    try:
        server = OscServer(osc_video)
    except ServerError, err:
        print str(err)
        sys.exit()

    server.start()
    osc_video.main_loop()

main()
