# pyOscVideo

pyOscVideo is a multi-video recorder and player controllable via [Open Sound Control (OSC)](https://opensoundcontrol.stanford.edu/).

The main purpose is to record video from multiple cameras synchronized with another source, for instance, another software recording audio. Since recording multiple videos in high resolution is a demanding task for the hardware, other tasks (audio recording, sensor data recording, measurements, dsp, etc.) can be performed on a separate computer and synchronized via OSC over the network.

pyOscVideo currently does not support Windows, recording of multiple high definition videos on GNU/Linux might depend on your build of OpenCV.

pyOscVideo is developed within the research project ["Social interaction through sound feedback – Sentire"](https://www.musikundmedien.hu-berlin.de/de/musikwissenschaft/systematik/projekte/sentire-soziale-interaktion-durch-klang-feedback)

## Install notes

You should be able to install directly from PyPI:

`pip install pyoscvideo`

Please note that you will need to install [VLC](https://www.videolan.org/vlc/) for the player functionality.

## Usage

After installing you can run it by typing:

`pyoscvideo` and `pyoscvideoplayer`

You can control both the recorder and the player via OSC or using the GUI.
To start the player with GUI control run as:

`$ pyoscvideoplayer --no-osc`

### Controlling the recorder

| OSC command                  | argument                   | description                                                                                                                   | reply (on success)                    |
|------------------------------|----------------------------|-------------------------------------------------------------------------------------------------------------------------------|---------------------------------------|
| `/oscVideo/prepareRecording` | string, the recording path | Prepares all the internal buffers for writing to filesystem but won't start recording. Sends a reply when finished preparing. | `/oscVideo/status Prepared Recording` |
| `/oscVideo/record`           | boolean                    | Starts/stops the recording. Sends a reply about the success of starting the recording                                         | `/oscVideo/status Started Recording`  |                                                                                                                         |                                       |

### Controlling the player

| OSC command                  | argument                  | description                                          |
|------------------------------|---------------------------|------------------------------------------------------|
| `/oscVideo/loadFolder`       | string, video folder path | Loads all videos inside the folder path              |
| `/oscVideo/loadFile`         | string, video file path   | Loads a video                                        |
| `/oscVideo/setVideoPlay`     |                           | Starts playing the videos                            |
| `/oscVideo/setVideoPause`    |                           | Pauses the player                                    |
| `/oscVideo/setVideoPosition` | time in milliseconds      | Sets playback position                               |
| `/oscVideo/clean`            |                           | Unloads / removes all loaded videos from the player |

## Development

* Check coding style (PEP-8) and type hints

* First need to install the tools (in case you don't have):
        pip install pycodestyle mypy 

* then simply run:
        ./run_tests.sh 
