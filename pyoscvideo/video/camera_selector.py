# *****************************************************************************
#  Copyright (c) 2020. Pascal Staudt, Bruno Gola                              *
#                                                                             *
#  This file is part of pyOscVideo.                                           *
#                                                                             *
#  pyOscVideo is free software: you can redistribute it and/or modify         *
#  it under the terms of the GNU General Public License as published by       *
#  the Free Software Foundation, either version 3 of the License, or          *
#  (at your option) any later version.                                        *
#                                                                             *
#  pyOscVideo is distributed in the hope that it will be useful,              *
#  but WITHOUT ANY WARRANTY; without even the implied warranty of             *
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              *
#  GNU General Public License for more details.                               *
#                                                                             *
#  You should have received a copy of the GNU General Public License          *
#  along with pyOscVideo.  If not, see <https://www.gnu.org/licenses/>.       *
# *****************************************************************************

import logging
import platform
import re
import subprocess
import sys

from typing import Dict, Type

from PyQt5.QtCore import QObject, pyqtSignal
from pyoscvideo.video.camera import Camera

if platform.system() == "Linux":
    import pyudev
    import pyoscvideo.helpers.v4l2 as v4l2
    import fcntl


class BaseCameraSelector(QObject):
    """
    Base class for dealing with camera selection and handling, shouldn't be
    used directly but as inherited by specialized classes depending on the
    operating system.

    Camera Selector is responsible for keeping track of cameras
    available to capture from and keeping the current selected camera.
    """
    camera_list_cleared = pyqtSignal()
    camera_removed = pyqtSignal(object)
    camera_added = pyqtSignal(object)

    cameras: Dict[int, Camera]

    def __init__(self) -> None:
        super().__init__()
        self._logger = logging.getLogger(__name__+".CameraSelector")
        self.cameras = {}

        self.find_cameras()

    def add_camera(self, number: int, name: str):
        self._logger.info(f"New camera added: {name} - {number}")
        self.cameras[number] = Camera(number, name)
        self.camera_added.emit(self.cameras[number])

    def remove_camera(self, number: int):
        camera = self.cameras[number]
        self._logger.info(
                f"Camera removed: {camera.name} - {camera.device_id}")
        del self.cameras[number]
        self.camera_removed.emit(camera)

    def find_cameras(self):
        raise NotImplementedError


class OSXCameraSelector(BaseCameraSelector):
    """
    Specialized camera selector for OS X operating system.
    """
    def find_cameras(self):
        """
        Populates with cameras available for capturing.
        """
        # TODO: should use ctypes and the IOKit on OS X so we don't depend
        # on opening a subprocess to check for cameras and can also be
        # notified in real-time when cameras are added/removed.
        camera_dict = {}
        output = subprocess.check_output(
                ['system_profiler', 'SPCameraDataType'])
        p = re.compile(r"\s{4}([^\\n]+):\\n\\n")
        device_list = p.findall(str(output))
        self._logger.info("Found %s cameras", len(device_list))
        for camera_id, camera_name in enumerate(device_list):
            camera_dict[camera_id] = camera_name
            self._logger.info("[%s] %s", camera_id, camera_name)
            self.add_camera(int(camera_id), camera_name)


class LinuxCameraSelector(BaseCameraSelector):
    """
    Specialized camera selector for Linux operating system. Uses udev.
    """
    def __init__(self):
        # Sets up udev context so we can find cameras
        self._udev_ctx = pyudev.Context()
        self._udev_observer = None

        super().__init__()

        # Start observing for new cameras added or removed
        self._setup_udev_observer()

    def _setup_udev_observer(self):
        monitor = pyudev.Monitor.from_netlink(self._udev_ctx)
        monitor.filter_by("video4linux")
        self._udev_observer = pyudev.MonitorObserver(
                monitor, self._udev_observer_callback)
        self._udev_observer.start()
        self._logger.info(f"udev monitor started")

    def _udev_observer_callback(self, action: str, device: pyudev.Device):
        self._logger.info(f"New udev action: {action} - {device}")
        if action == "add":
            if self._check_capture_capability(device):
                self._add_camera(device)
        elif action == "remove":
            if int(device.sys_number) in self.cameras.keys():
                self._remove_camera(device)

    def _check_capture_capability(self, device: pyudev.Device) -> bool:
        """
        Check if {device} is capable of capturing.
        """
        with open(device.device_node) as fd:
            cp = v4l2.v4l2_capability()
            # Ignore type checking here because ioctl apparenlty can't handle
            # a ctypes.Structure
            fcntl.ioctl(fd, v4l2.VIDIOC_QUERYCAP, cp)  # type: ignore
        return cp.device_caps & v4l2.V4L2_CAP_VIDEO_CAPTURE

    def _add_camera(self, device: pyudev.Device):
        self._logger.info(f"Device added: {device}")
        self.add_camera(
                int(device.sys_number),
                device.attributes.get("name").decode(sys.stdout.encoding))

    def _remove_camera(self, device: pyudev.Device):
        self._logger.info(f"Device removed: {device}")
        self.remove_camera(int(device.sys_number))

    def find_cameras(self):
        """
        Populates with cameras available for capturing.
        """
        self._logger.info(f"Finding cameras")
        for device in self._udev_ctx.list_devices(subsystem="video4linux"):
            if self._check_capture_capability(device):
                self._add_camera(device)


# CameraSelector is a Singleton, keeping track of all
# cameras recognized by the OS.
CameraSelector: Type[BaseCameraSelector]
if platform.system() == "Linux":
    CameraSelector = LinuxCameraSelector()
elif platform.system() == "Darwin":
    CameraSelector = OSXCameraSelector()
