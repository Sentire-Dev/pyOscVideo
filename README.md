# pyOscVideo

pyOscVideo is a multi-video recorder and player controllable via [Open Sound Control (OSC)](https://opensoundcontrol.stanford.edu/).

The main purpose is to record video from multiple cameras synchronized with another source, for instance another software recording an audio source. Since recording multiple videos in high resolution is a demanding task for the hardware, other tasks (audio recording, sensor data recording, measurements, dsp, etc.) can be performed on a separate computer and synchronized via OSC over the network.

pyOscVideo is developed within the research project ["Social interaction through sound feedback – Sentire"](https://www.musikundmedien.hu-berlin.de/de/musikwissenschaft/systematik/projekte/sentire-soziale-interaktion-durch-klang-feedback)

## Install notes

You should be able to install directly from PyPI:

`pip install pyoscvideo`



Please note that you will need to install VLC for the player functionality.

## Usage

After installing you can run it by typing:

`pyoscvideo` and `pyoscvideoplayer`


### Controlling the recorder

To control the recorder you need to send the following OSC messages:

* /oscVideo/prepareRecording
    Receives as an argument a path where to record the video files.
    This will prepare all the internal buffers for writing to filesystem but won't start recording.
    When pyOscVideo is done preparing the buffers it will reply with `/oscVideo/status` and the string 
    `Prepared Recording` as an argument.

* /oscVideo/record
   the first argument is a boolean that will define if it should start or stop recording.

### Controlling the player

For the player the following OSC messages are valid:

* /oscVideo/loadFolder
    Will load all videos inside the folder sent as the first argument

* /oscVideo/setVideoPlay
    Starts playing the videos

* /oscVideo/setVideoPause
    Pauses the player

* /oscVideo/setVideoPosition
    Set all videos to the position specified by the first argument (as time in milliseconds)

* /oscVideo/clean
    Unloades / removes all loaded videos from the player

## Development

* Check coding style (PEP-8) and type hints

* First need to install the tools (in case you don't have):
        pip install pycodestyle mypy 

* then simply run:
        ./run_tests.sh 
