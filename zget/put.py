#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, \
    unicode_literals
import os
import sys
import time
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


def validate_address(address):
    try:
        socket.inet_aton(address)
        return address
    except socket.error:
        raise argparse.ArgumentTypeError(
            "%s is not a valid IP address" % address
        )


class FileHandler(BaseHTTPRequestHandler):
    """
    Custom HTTP upload handler that allows one single filename to be requested.

    """
    filename = ""
    basename = ""
    reporthook = None

    def do_GET(self):
        if self.path == urllib.pathname2url(os.path.join('/', self.basename)):
            utils.logger.info("Peer found. Uploading...")
            full_path = os.path.join(os.curdir, self.filename)
            with open(full_path, 'rb') as fh:
                maxsize = os.path.getsize(full_path)
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.send_header('Content-length', maxsize)
                self.end_headers()

                i = 0
                while True:
                    data = fh.read(1024 * 8)  # chunksize taken from urllib
                    if not data:
                        break
                    self.wfile.write(data)
                    if self.reporthook is not None:
                        self.reporthook(i, 1024 * 8, maxsize)
                    i += 1

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
        type=validate_address,
        help="The address to share the file on."
    )
    parser.add_argument(
        '--interface', '-i', nargs='?',
        help="The interface to share the file on."
    )
    parser.add_argument(
        '--verbose', '-v',
        action='count', default=0,
        help="Set verbosity level, to show debug info."
    )
    parser.add_argument(
        '--quiet', '-q',
        action='count', default=0,
        help="Set quietness level, to hide progess bar."
    )
    parser.add_argument(
        '--timeout', '-t',
        type=int,
        help="Set timeout after which program aborts transfer."
    )
    parser.add_argument(
        'input',
        help="The file to share on the network"
    )
    args = parser.parse_args(inargs)

    utils.enable_logger(args.verbose)

    progress = utils.Progresshook()
    try:
        if args.interface and args.address:
            raise ValueError(
                "You may only provide one of --address "
                "or --interface"
            )

        put(
            args.input,
            interface=args.interface,
            address=args.address,
            port=args.port,
            reporthook=progress.update if args.quiet == 0 else None,
            timeout=args.timeout,
        )
    except Exception as e:
        utils.logger.error(e.message)
        sys.exit(1)
    progress.finish()


def put(
    filename,
    interface=None,
    address=None,
    port=None,
    reporthook=None,
    timeout=None,
):
    """
    Actual logic for sending files

    """
    if port is None:
        port = utils.config().getint('DEFAULT', 'port')

    if interface is None:
        interface = utils.config().get('DEFAULT', 'interface')

    if not 0 <= port <= 65535:
        raise ValueError("Port %d exceeds allowed range" % port)

    basename = os.path.basename(filename)
    filehash = hashlib.sha1(basename.encode('utf-8')).hexdigest()

    if address is None:
        address = utils.ip_addr(interface)

    server = HTTPServer((address, port), FileHandler)
    server.timeout = timeout
    server.RequestHandlerClass.filename = filename
    server.RequestHandlerClass.basename = basename
    server.RequestHandlerClass.reporthook = reporthook

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
    start_time = time.time()
    try:
        zeroconf.register_service(info)

        server.handle_request()
        utils.logger.info("Done.")
    except KeyboardInterrupt:
        pass

    if timeout is not None and time.time() - start_time > timeout:
        utils.logger.info("Timeout.")
        sys.exit(1)

    server.socket.close()
    zeroconf.unregister_service(info)
    zeroconf.close()

if __name__ == '__main__':
    cli(sys.argv[1:])
