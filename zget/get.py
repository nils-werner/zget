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

from zeroconf import ServiceBrowser, Zeroconf

from . import utils

__all__ = ["get"]


class ServiceListener(object):
    """
    Custom zeroconf listener that is trying to find the service we're looking
    for.

    """
    filehash = ""
    address = None
    port = False

    def remove_service(*args):
        pass

    def add_service(self, zeroconf, type, name):
        if name == self.filehash + "._zget._http._tcp.local.":
            utils.logger.info("Peer found. Downloading...")
            info = zeroconf.get_service_info(type, name)
            if info:
                self.address = socket.inet_ntoa(info.address)
                self.port = info.port


def cli(inargs=None):
    """
    Commandline interface for receiving files

    """
    parser = argparse.ArgumentParser()

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
        'filename',
        help="The filename to look for on the network"
    )
    parser.add_argument(
        'output',
        nargs='?',
        help="The local filename to save to"
    )
    args = parser.parse_args(inargs)

    utils.enable_logger(args.verbose)

    try:
        with utils.Progresshook() as progress:
            get(
                args.filename,
                args.output,
                reporthook=progress if args.quiet == 0 else None,
                timeout=args.timeout
            )
    except Exception as e:
        if args.verbose:
            raise
        utils.logger.error(e.message)
        sys.exit(1)


def get(
    filename,
    output=None,
    reporthook=None,
    timeout=None
):
    """
    Actual logic for receiving files. May be imported and called from other
    modules, too.

    """
    basename = os.path.basename(filename)
    filehash = hashlib.sha1(basename.encode('utf-8')).hexdigest()
    if output is None:
        output = filename

    zeroconf = Zeroconf()
    listener = ServiceListener()
    listener.filehash = filehash

    utils.logger.debug("Looking for " + filehash + "._zget._http._tcp.local.")

    browser = ServiceBrowser(zeroconf, "_zget._http._tcp.local.", listener)

    start_time = time.time()
    try:
        while listener.address is None:
            time.sleep(0.5)
            if (
                timeout is not None and
                time.time() - start_time > timeout
            ):
                raise utils.TimeoutException()

        utils.logger.debug(
            "Downloading from %s:%d" % (listener.address, listener.port)
        )
        url = "http://" + listener.address + ":" + str(listener.port) + "/" + \
              urllib.pathname2url(filename)

        urllib.urlretrieve(
            url, output,
            reporthook=reporthook
        )
    except KeyboardInterrupt:
        pass
    utils.logger.info("Done.")
    zeroconf.close()

if __name__ == '__main__':
    cli(sys.argv[1:])
