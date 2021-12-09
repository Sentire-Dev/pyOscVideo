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
    parser = argparse.ArgumentParser(description='OSC example controller for pyOscVideo.')
    parser.add_argument('--prepare-recording', type=str, dest="folder",
                        help='Prepares recording to the specified folder')
    parser.add_argument('--record', dest='record', action='store_const', const=True,
                        help='Start recording')
    parser.add_argument('--stop', dest='stop', action='store_const', const=True,
                        help='Stop recording')

    args = parser.parse_args(sys.argv[1:])
    
    ip = "127.0.0.1"
    port = 57220
    
    client = SimpleUDPClient(ip, port)  # Create client

    if args.folder:
        client.send_message("/oscVideo/prepareRecording", args.folder)
    elif args.record:
        client.send_message("/oscVideo/record", True)
    elif args.stop:
        client.send_message("/oscVideo/record", False)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


