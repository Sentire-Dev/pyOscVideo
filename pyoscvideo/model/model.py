from PyQt5.QtCore import QObject, pyqtSignal
import logging


class BaseModel(QObject):
    def __new__(cls):
        # Sets a dynamic `_signals` class variable, an array
        # with all attributes monitored with signals by this class
        cls._signals = [
            attr[:attr.rfind("_changed")] for attr in
                 cls.__dict__.keys() if attr.endswith("_changed") and
                    isinstance(getattr(cls, attr), pyqtSignal) ]
        return super().__new__(cls)

    def __setattr__(self, attr, value):
        # Checks if attribute should emit a signal when being set.
        if attr in self._signals:
            getattr(self, attr + "_changed").emit(value)
        return super().__setattr__(attr, value)


class Recorder(BaseModel):
    is_capturing_changed = pyqtSignal(bool)
    frame_rate_changed = pyqtSignal(float)
    status_msg_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".Recorder")
        self._status_msg = ''
        self.is_capturing = False
        self.frame_rate = 30
        self.frame_counter = 0
        self.last_update = 0


class CameraSelectorModel(BaseModel):
    selection_changed = pyqtSignal(int)
    camera_list_cleared = pyqtSignal()
    camera_removed = pyqtSignal(object)
    camera_added = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__ + ".CameraSelectorModel")
        self._cameras = {}
        self.selection = None

    def add_camera(self, number, name):
        self._logger.info(f"New camera added: {name} - {number}")
        self._cameras[number] = name
        self.camera_added.emit({'number': number, 'name': name})

    def remove_camera(self, number):
        name = self._cameras[number]
        self._logger.info(f"Camera removed: {name} - {number}")
        del self._cameras[number]
        self.camera_removed.emit({'number': number, 'name': name})
