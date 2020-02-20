from PyQt5.QtCore import QObject, pyqtSignal

class CameraSelectionModel(QObject):
    selection_changed = pyqtSignal(str)
    clear_camera_list = pyqtSignal()
    add_camera = pyqtSignal(str)
    cameras_changed = pyqtSignal(list)
    even_odd_changed = pyqtSignal(str)
    enable_reset_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._cameras = []
        self._selection = 0

    @property
    def selection(self):
        """Return the selected device id."""
        return self._selection

    @selection.setter
    def selection(self, camera_name):
        """Set the capturing status."""
        self._selection = camera_name
        self.selection_changed.emit(camera_name)

    @property
    def cameras(self):
        """Return the available cameras."""
        return self._cameras

    @cameras.setter
    def cameras(self, cam_dict):
        """Set the available camera.
        
        Value has to equal device ID
        """
        self._cameras = cam_dict
        self.clear_camera_list.emit()
        for name in cam_dict:
            self.add_camera.emit(name)

