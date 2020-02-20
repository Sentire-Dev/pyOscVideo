import logging.config
import os
import json
import cv2


def setup_logging(default_path='pyoscvideo/logging/logging_settings.json',
                  default_level=logging.INFO, ):
    """Set up logging configuration."""
    path = default_path
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
