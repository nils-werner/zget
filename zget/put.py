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
import logging

from zeroconf import ServiceInfo, Zeroconf
try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from . import utils

__all__ = ["put"]


class FileHandler(BaseHTTPRequestHandler):
    """
    Custom HTTP upload handler that allows one single filename to be requested.

    """
    filename = ""
    basename = ""

    def do_GET(self):
        if self.path == urllib.pathname2url(os.path.join('/', self.basename)):
            utils.logger.info("Peer found. Uploading...")
            with open(os.path.join(os.curdir, self.filename), 'rb') as fh:
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()

                while True:
                    data = fh.read(2 ** 20)  # Read 1 MB of input file
                    if not data:
                        break
                    self.wfile.write(data)

        else:
            self.send_response(404)
            self.end_headers()
            raise RuntimeError("Invalid request received. Aborting.")

    def log_message(self, format, *args):
        """
        Suppress log messages by overloading this function

        """
        return


def cli(inargs=None):
    """
    Commandline interface for sending files

    """
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

    if args.verbose:
        utils.enable_logger(logging.DEBUG)
    else:
        utils.enable_logger()

    put(args.input, args.port)


def put(filename, port=None):
    """
    Actual logic for sending files

    """
    if port is None:
        port = utils.config().getint('DEFAULT', 'port')

    if not 0 <= port <= 65535:
        raise ValueError("Port %d exceeds allowed range" % port)

    basename = os.path.basename(filename)
    filehash = hashlib.sha1(basename.encode('utf-8')).hexdigest()

    ip = socket.gethostbyname(socket.gethostname())
    server = HTTPServer(('', port), FileHandler)
    server.RequestHandlerClass.filename = filename
    server.RequestHandlerClass.basename = basename

    port = server.server_port

    utils.logger.debug(
        "Listening on %s:%d, you may change port using --port" % (ip, port)
    )

    utils.logger.debug(
        "Broadcasting as %s._zget._http._tcp.local." % filehash
    )

    info = ServiceInfo(
        "_zget._http._tcp.local.",
        "%s._zget._http._tcp.local." % filehash,
        socket.inet_aton(ip), port, 0, 0,
        {'path': None}
    )

    zeroconf = Zeroconf()
    zeroconf.register_service(info)

    server.handle_request()
    utils.logger.info("Done.")

    zeroconf.unregister_service(info)
    zeroconf.close()


if __name__ == '__main__':
    cli(sys.argv[1:])
