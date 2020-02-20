from PyQt5.QtCore import QObject, pyqtSignal


class Model(QObject):
    is_capturing_changed = pyqtSignal(bool)
    status_msg_changed = pyqtSignal(str)
    even_odd_changed = pyqtSignal(str)
    enable_reset_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._is_capturing = False
        self._even_odd = ''
        self._enable_reset = False
        self._status_msg = ''
        self._frame_rate = 30
        self.frame_counter = 0
        self.last_update = 0

    @property
    def frame_rate(self):
        """Return the frame rate."""
        return self._frame_rate

    @frame_rate.setter
    def frame_rate(self, fps):
        """Set the frame rate."""
        self._frame_rate = fps


    @property
    def is_capturing(self):
        """Return the capturing status."""
        return self._is_capturing

    @is_capturing.setter
    def is_capturing(self, value):
        """Set the capturing status."""
        self._is_capturing = value
        self.is_capturing_changed.emit(value)

    @property
    def status_msg(self):
        """Return the status message."""
        return self._status_msg

    @status_msg.setter
    def status_msg(self, msg):
        """Set the status message."""
        self._status_msg = msg
        self.status_msg_changed.emit(msg)

    @property
    def even_odd(self):
        return self._even_odd

    @even_odd.setter
    def even_odd(self, value):
        self._even_odd = value
        self.even_odd_changed.emit(value)

    @property
    def enable_reset(self):
        return self._enable_reset

    @enable_reset.setter
    def enable_reset(self, value):
        self._enable_reset = value
        self.enable_reset_changed.emit(value)