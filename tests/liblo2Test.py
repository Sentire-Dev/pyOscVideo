#!/usr/bin/env python3

from liblo import ServerThread, make_method, ServerError
import sys

class MyServer(ServerThread):
    def __init__(self):
        ServerThread.__init__(self, 1234)

    @make_method('/foo', 'ifs')
    def foo_callback(self, path, args):
        i, f, s = args
        print ("received message '%s' with arguments: %d, %f, %s" % (path, i, f, s))

    @make_method(None, None)
    def fallback(self, path, args):
        print ("received unknown message '%s'" % path)

try:
    server = MyServer()
except ServerError as err:
    print (str(err))
    sys.exit()

server.start()
raw_input("press enter to quit...\n")
