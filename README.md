# pyOscVideo

## Install notes

### Mac
* Install python 3

* create virtual environment

# macOS/Linux

* You may need to run sudo apt-get install python3-venv first

        python3 -m venv .venv

* activate virtual environment

        source .venv/bin/activate

* Install dependencies (requirements.txt): 

        pip install -r requirements.txt 

* Generate UI code from .ui file

        pyuic5 pyoscvideo/ressources/main_view.ui -o pyoscvideo/views/main_view_ui.py

* Install pyOscVideo locally

        pip install -e .
        
* run with:

        pyoscvideo


## Development

* Check coding style (PEP-8):

        pip install pycodestyle
        pycodestyle --exclude v4l2.py,main_view_ui.py pyoscvideo/
