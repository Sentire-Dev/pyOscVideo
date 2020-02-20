import platform
import os
import subprocess
import re
import logging
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
from pyoscvideo.model.camera_selection_model import CameraSelectionModel

class CameraSelector(QObject):
    """The main controller object.
    
    TODO:
    """
    selection_changed = pyqtSignal(int)

    def __init__(self, model, view):
        """Init the camera selection controller.
        
        Arguments:
            model {QObject} -- [The model]
        
        Raises:
            InitError: If CameraReader could not be initialized correctly
        """
        super().__init__()
        self._logger = logging.getLogger(__name__+".CameraSelector")
        self._logger.info("Initializing")
        self._view = view
        
        self._model = model
        self._model.clear_camera_list.connect(self._view.clear)
        self._model.add_camera.connect(self._view.addItem)

        self._camera_dict = {}
                
        self._view.currentTextChanged.connect(self.change_selection)
        self._add_camera_counter = 0
        self._duplicate_regex = re.compile(r".+\[(\d+)\]", re.IGNORECASE)
        self.find_cameras()

    
    def find_cameras(self):
        self._camera_dict = {}
        camera_names = []
        if platform.system() == 'Darwin':
            output = subprocess.check_output(['system_profiler', 'SPCameraDataType'])
            p = re.compile(r"\s{4}([^\\n]+):\\n\\n")
            device_list = p.findall(str(output))
            self._logger.info("Found %s cameras", len(device_list))
            for camera_id, camera_name in enumerate(device_list):
                camera_name_inc = self.add_to_dict_with_key_increment(self._camera_dict, camera_name, camera_id)
                camera_names.append(camera_name_inc)
                self._logger.info("[%s] %s", camera_id, camera_name)

        if platform.system() == "Linux":
            dir_str = '/sys/class/video4linux/'
            directory = os.fsencode(dir_str)
            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                output = os.popen("cat " + dir_str + filename + '/name').read()
                camera_name = output[:len(output) - 1]
                camera_id = int(filename[5])
                #self._logger.info("[%s] %s", camera_id, camera_name)
                camera_name_inc = self.add_to_dict_with_key_increment(self._camera_dict, camera_name, camera_id)
                camera_names.append(camera_name_inc)
        camera_names.sort()
        self._model.cameras = camera_names

    @property
    def selected_camera(self):
        """Return the device id of the selected camera
        
        Returns:
            int -- the device id
        """
        return self._camera_dict[self._model.selection]


    def add_to_dict_with_key_increment(self, dictionary, key, value):
        """Add a key value pair to a given dictionary.

        If the key already exists the key is incremented: key becomes key [1], key [1] becomes key [2]...

        Note: key needs to be of type str
        
        Arguments:
            dictionary {dict} -- The dictionary
            key {str} -- The key. Needs to be of type str
            value {object} -- The value

        Returns:
            str -- the (incremented) key for the stored value
        """
        if not isinstance(key, str):
            raise TypeError(key)
        if not key in dictionary:
            dictionary[key] = value
        else:
            counter = 0
            for item in dictionary:
                if not re.search("^" + key, item) is None:
                    counter += 1
            key = key + " [" + str(counter) + "]"
            dictionary[key] = value
        return key

    @pyqtSlot(str)
    def change_selection(self, camera_name):
        """Change the selected camera.
        
        Arguments:
            camera_name {String} -- the name of the camera
        """
        if (camera_name in self._camera_dict):
            self._model.selection = camera_name
            self._logger.info("Selected camera: %s", camera_name)
            self.selection_changed.emit(self._camera_dict[camera_name])
        else:
            msg = "Camera %s is not a valid name." % camera_name
            self._logger.error(msg)
            raise KeyError(msg)



