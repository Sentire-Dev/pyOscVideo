#!/usr/bin/python
# *****************************************************************************
#  Copyright (c) 2021. Pascal Staudt, Bruno Gola                              *
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


import argparse, sys
from pythonosc.udp_client import SimpleUDPClient


def main():
    parser = argparse.ArgumentParser(description='OSC example controller for pyOscVideo player.')
    parser.add_argument('--load-folder', type=str, dest="folder",
                        help='Prepares recording to the specified folder')
    parser.add_argument('--play', dest='play', action='store_const', const=True,
                        help='Plays the loaded videos')
    parser.add_argument('--pause', dest='pause', action='store_const', const=True,
                        help='Pause the player')
    parser.add_argument('--position', dest='position', type=int,
                        help='Stop recording')
    parser.add_argument('--clean', dest='clean', action='store_const', const=True,
                        help='Clears the player')

    args = parser.parse_args(sys.argv[1:])
    
    ip = "127.0.0.1"
    port = 57221
    
    client = SimpleUDPClient(ip, port)  # Create client

    if args.folder:
        client.send_message("/oscVideo/loadFolder", args.folder)
    elif args.play:
        client.send_message("/oscVideo/setVideoPlay", [])
    elif args.pause:
        client.send_message("/oscVideo/setVideoPause", [])
    elif args.position is not None:
        client.send_message("/oscVideo/setVideoPosition", args.position)
    elif args.clean:
        client.send_message("/oscVideo/clean", [])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


