#!/bin/bash

for ui_file in pyoscvideo/gui/resources/*ui; do
    pyuic5 "${ui_file}" -o "$(echo ${ui_file} | sed 's/resources\///' | sed 's/.ui$/_ui.py/')"
done
