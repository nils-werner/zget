#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, \
    unicode_literals
import os
import sys
import socket
import hashlib
import argparse

from zeroconf import ServiceInfo, Zeroconf
try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


filename = ""
filehash = ""


class FileHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global filename, filehash
        if self.path == os.path.join('/', filename):
            print("Peer found. Uploading...")
            with open(os.path.join(os.curdir, filename), 'rb') as fh:
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                self.wfile.write(fh.read())
        else:
            print("Invalid request received. Aborting.")
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


def put(inargs=None):
    global filename, filehash

    parser = argparse.ArgumentParser()

    parser.add_argument(
        'input',
        help="The file to share on the network"
    )
    args = parser.parse_args(inargs)

    filename = args.input
    filehash = hashlib.sha1(filename.encode('utf-8')).hexdigest()

    ip = socket.gethostbyname(socket.gethostname())
    server = HTTPServer(('', 0), FileHandler)
    port = server.server_port

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
