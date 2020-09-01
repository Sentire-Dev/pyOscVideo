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

from typing import Dict, Any

import logging
import os.path
import yaml


_logger = logging.getLogger("Settings")


def _remove_unused_configuration(
        loaded: Dict[str, Any],
        default: Dict[str, Any]):
    for k, v in list(loaded.items()):
        if k not in default.keys():
            # ignore settings that we don't support
            _logger.warning(f"Unknow config option: {k}")
            del loaded[k]
        else:
            if isinstance(v, dict):
                _remove_unused_configuration(v, default[k])


def load_settings(path: str):
    """
    Loads YAML settings file.
    """
    # Default settings:
    settings: Dict[str, Any] = {
            'osc': {
                'address': '0.0.0.0',
                'port': 57220,
                'remote_address': '127.0.0.1',
                'remote_port': 57210,
                },
            'gui': {
                'enabled': True,
                'num_cameras': 1,
                },
            'camera': {
                'recording_fps': 25,
                'codec': 'MJPG',
                'resolution': {
                    'width': 1920,
                    'height': 1080,
                },
                'recording_resolution': {
                    'width': 1280,
                    'height': 720,
                },
            }
        }

    if os.path.exists(path):
        with open(path) as settings_file:
            loaded_settings = yaml.safe_load(settings_file)
            _remove_unused_configuration(loaded_settings, settings)
            settings.update(loaded_settings)
    else:
        _logger.warning(f"Can't find settings file: '{path}'")

    # remove GUI configuration if it is not enabled
    if not settings.get('gui', {}).pop('enabled', True):
        settings.pop('gui', {})
    return settings
