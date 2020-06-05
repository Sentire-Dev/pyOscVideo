#!/bin/bash

pycodestyle --exclude v4l2.py,main_view_ui.py,camera_view_ui.py pyoscvideo/ && mypy pyoscvideo/__main__.py
