"""Lists the available video devices on several platforms.

Test file for parsing available video devices on MacOs and Linux

TODO:
    * add Windows implementation

Version:
    0.1

Author:
    Pascal Staudt

License:
    Copyright (C) 2020 Pascal Staudt
    This file is part of oscvideo software.
    oscvideo is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the Free
    Software Foundation, either version 3 of the License, or (at your option) any
    later version.
    oscvideo software is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
    more details.
    You should have received a copy of the GNU General Public License along with
    oscvideo software. If not, see <http://www.gnu.org/licenses/>.
"""
import platform
import os
import subprocess
import re
# pylint: disable=C0103
# pylint: disable=global-statement
if platform.system() == 'Darwin':
    output = subprocess.check_output(['system_profiler', 'SPCameraDataType'])
    p = re.compile(r"\s{4}([^\\n]+):\\n\\n")
    device_list = p.findall(str(output))
    print("size: " + str(len(device_list)))
    for i, item in enumerate(device_list):
        print(str(i) + ": " + item)

if platform.system() == "Linux":
    dir_str = '/sys/class/video4linux/'
    directory = os.fsencode(dir_str)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        output = os.popen("cat " + dir_str + filename + '/name').read()
        camera_name = output[:len(output) - 1]
        camera_id = filename[5]
        print("[%s] %s"  % (camera_id, camera_name))
