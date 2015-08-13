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
        '--address', '-a', nargs='?',
        help="The address to share the file on."
    )
    parser.add_argument(
        '--interface', '-i', nargs='?',
        help="The interface to share the file on."
    )
    parser.add_argument(
        '--verbose', '-v',
        action='count', default=0,
        help="Set verbosity level."
    )
    parser.add_argument(
        'input',
        help="The file to share on the network"
    )
    args = parser.parse_args(inargs)

    utils.enable_logger(args.verbose)

    try:
        if args.interface and args.address:
            raise ValueError(
                "You may only provide one of --address "
                "or --interface"
            )

        put(args.input, args.interface, args.address, args.port)
    except Exception as e:
        utils.logger.error(e.message)
        sys.exit(1)


def put(filename, interface=None, address=None, port=None):
    """
    Actual logic for sending files

    """
    if port is None:
        port = utils.config().getint('DEFAULT', 'port')

    if not 0 <= port <= 65535:
        raise ValueError("Port %d exceeds allowed range" % port)

    basename = os.path.basename(filename)
    filehash = hashlib.sha1(basename.encode('utf-8')).hexdigest()

    if address is None:
        address = utils.ip_addr(interface)

    server = HTTPServer((address, port), FileHandler)
    server.RequestHandlerClass.filename = filename
    server.RequestHandlerClass.basename = basename

    port = server.server_port

    utils.logger.debug(
        "Listening on %s:%d \n"
        "you may change address using --address and "
        "port using --port" % (address, port)
    )

    utils.logger.debug(
        "Broadcasting as %s._zget._http._tcp.local." % filehash
    )

    info = ServiceInfo(
        "_zget._http._tcp.local.",
        "%s._zget._http._tcp.local." % filehash,
        socket.inet_aton(address), port, 0, 0,
        {'path': None}
    )

    zeroconf = Zeroconf()
    try:
        zeroconf.register_service(info)

        server.handle_request()
        utils.logger.info("Done.")
    except KeyboardInterrupt:
        pass

    zeroconf.unregister_service(info)
    zeroconf.close()

if __name__ == '__main__':
    cli(sys.argv[1:])
