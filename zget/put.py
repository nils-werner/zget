#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, \
    unicode_literals
import os
import sys
import socket
try:
    import urllib.request as urllib
except ImportError:
    import urllib
import hashlib
import argparse

from zeroconf import ServiceInfo, Zeroconf
try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from . import utils

filename = ""
basename = ""
filehash = ""


class FileHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global filename, basename, filehash
        if self.path == urllib.pathname2url(os.path.join('/', basename)):
            print("Peer found. Uploading...")
            with open(os.path.join(os.curdir, filename), 'rb') as fh:
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()

                while True:
                    data = fh.read(2 ** 20)  # Read 1 MB of input file
                    if not data:
                        break
                    self.wfile.write(data)

        else:
            print("Invalid request received. Aborting.")
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def put(inargs=None):
    global filename, basename, filehash

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--port', '-p',
        type=int, nargs='?',
        help="The port to share the file on."
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help="Enable debug messages."
    )
    parser.add_argument(
        'input',
        help="The file to share on the network"
    )
    args = parser.parse_args(inargs)

    if args.port is None:
        args.port = utils.config().getint('DEFAULT', 'port')

    if not 0 <= args.port <= 65535:
        raise ValueError("Port %d exceeds allowed range" % args.port)

    filename = args.input
    basename = os.path.basename(filename)
    filehash = hashlib.sha1(basename.encode('utf-8')).hexdigest()

    ip = socket.gethostbyname(socket.gethostname())
    server = HTTPServer(('', args.port), FileHandler)
    port = server.server_port

    if args.verbose:
        print(
            "Listening on %s:%d, you may change port using --port"
            % (ip, port)
        )

    info = ServiceInfo("_zget._http._tcp.local.",
                       filehash + "._zget._http._tcp.local.",
                       socket.inet_aton(ip), port, 0, 0,
                       {'path': None})

    zeroconf = Zeroconf()
    zeroconf.register_service(info)

    server.handle_request()
    print("Done.")

    zeroconf.unregister_service(info)
    zeroconf.close()


if __name__ == '__main__':
    put(sys.argv[1:])
