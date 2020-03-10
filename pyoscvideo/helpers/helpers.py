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

# pylint: disable=trailing-whitespace


import json
import logging.config
import os

import cv2


def setup_logging(settings_path='logging/logging_settings.json',
                  default_level=logging.INFO, ):
    """Set up logging configuration."""
    module_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(module_dir, settings_path)
    if os.path.exists(path):
        with open(path, 'rt') as config_file:
            config = json.load(config_file)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        print('Could not find: ' + str(path))


def get_cv_cap_property_id(cv_property):
    """Retrieve the OpenCV property (Integer) value."""
    integer_value = 0
    try:
        integer_value = getattr(cv2, cv_property)
    except AttributeError:
        print('{} is not a valid OpenCV property!'.format(cv_property))
        return None
    return integer_value
