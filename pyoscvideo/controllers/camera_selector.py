"""
    TODO: add file description
"""

# ******************************************************************************
#  Copyright (c) 2020. Pascal Staudt, Bruno Gola                               *
#                                                                              *
#  This file is part of pyOscVideo.                                            *
#                                                                              *
#  pyOscVideo is free software: you can redistribute it and/or modify          *
#  it under the terms of the GNU General Public License as published by        *
#  the Free Software Foundation, either version 3 of the License, or           *
#  (at your option) any later version.                                         *
#                                                                              *
#  pyOscVideo is distributed in the hope that it will be useful,               *
#  but WITHOUT ANY WARRANTY; without even the implied warranty of              *
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               *
#  GNU General Public License for more details.                                *
#                                                                              *
#  You should have received a copy of the GNU General Public License           *
#  along with pyOscVideo.  If not, see <https://www.gnu.org/licenses/>.        *
# ******************************************************************************

import logging
import platform
import re
import subprocess
import sys

from PyQt5.QtCore import QObject, pyqtSignal

if platform.system() == "Linux":
    import pyudev
    import pyoscvideo.helpers.v4l2 as v4l2
    import fcntl


class BaseCameraSelector(QObject):
    """The main controller object.

    TODO:
    """
    selection_changed = pyqtSignal(int)

    def __init__(self, model):
        """Init the camera selection controller.

        Arguments:
            model {QObject} -- [The model]

        Raises:
            InitError: If CameraReader could not be initialized correctly
        """
        super().__init__()
        self._logger = logging.getLogger(__name__+".CameraSelector")
        self._logger.info("Initializing")

        self._model = model
        self.find_cameras()


class OSXCameraSelector(BaseCameraSelector):
    def find_cameras(self):
        camera_dict = {}
        output = subprocess.check_output(
                ['system_profiler', 'SPCameraDataType'])
        p = re.compile(r"\s{4}([^\\n]+):\\n\\n")
        device_list = p.findall(str(output))
        self._logger.info("Found %s cameras", len(device_list))
        for camera_id, camera_name in enumerate(device_list):
            camera_dict[camera_id] = camera_name
            self._logger.info("[%s] %s", camera_id, camera_name)
            self._model.add_camera(int(camera_id), camera_name)


class LinuxCameraSelector(BaseCameraSelector):
    def __init__(self, model):
        # Sets up udev context so we can find cameras
        self._udev_ctx = pyudev.Context()
        self._udev_observer = None

        super().__init__(model)

        # Start observing for new cameras added or removed
        self._setup_udev_observer()

    def _setup_udev_observer(self):
        monitor = pyudev.Monitor.from_netlink(self._udev_ctx)
        monitor.filter_by("video4linux")
        self._udev_observer = pyudev.MonitorObserver(
                monitor, self._udev_observer_callback)
        self._udev_observer.start()
        self._logger.info(f"udev monitor started")

    def _udev_observer_callback(self, action, device):
        self._logger.info(f"New udev action: {action} - {device}")
        if action == "add":
            if self._check_capture_capability(device):
                self._add_camera(device)
        elif action == "remove":
            if int(device.sys_number) in self._model._cameras.keys():
                self._remove_camera(device)

    def _check_capture_capability(self, device):
        """
        Check if {device} is capable of capturing.

        Returns:
            bool -- capable of capturing or not
        """
        with open(device.device_node) as fd:
            cp = v4l2.v4l2_capability()
            fcntl.ioctl(fd, v4l2.VIDIOC_QUERYCAP, cp)
        return cp.device_caps & v4l2.V4L2_CAP_VIDEO_CAPTURE

    def _add_camera(self, device):
        self._logger.info(f"Device added: {device}")
        self._model.add_camera(
                int(device.sys_number),
                device.attributes.get("name").decode(sys.stdout.encoding))

    def _remove_camera(self, device):
        self._logger.info(f"Device removed: {device}")
        self._model.remove_camera(int(device.sys_number))

    def find_cameras(self):
        self._logger.info(f"Finding cameras")
        for device in self._udev_ctx.list_devices(subsystem="video4linux"):
            if self._check_capture_capability(device):
                self._add_camera(device)


if platform.system() == "Linux":
    CameraSelector = LinuxCameraSelector
elif platform.system() == "Darwin":
    CameraSelector = OSXCameraSelector
