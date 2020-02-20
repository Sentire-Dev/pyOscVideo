# pyOscVideo

## Install notes

### Mac
* Install liblo
        brew install liblo

* Install python 3

* create virtual environment

# macOS/Linux
# You may need to run sudo apt-get install python3-venv first
        python3 -m venv .venv

* activate virtual environment
        source .venv/bin/activate

* Install dependencies (requirements.txt): 

        pip install -R requirements.txt 

* **OR manually**

* Install Cython (requirement for pyliblo)

        python3 -m pip install Cython --install-option="--no-cython-compile"

* Install pyliblo
        pip install pyliblo

* Install pyliblo (see https://github.com/dsacre/pyliblo)

* Install opencv:

        pip install opencv-python

* if you are using pylint see https://github.com/PyCQA/pylint/issues/2426

echo /usr/local/opt/opencv/lib/python3.7/site-packages >> /usr/local/lib/python3.7/site-packages/opencv3.pth

* install qt
        pip install pyqt5


pyuic5 pyoscvideo/ressources/main_view.ui -o pyoscvideo/views/main_view_ui.py


* run with:

        pip install -e .
        pyoscvideo



