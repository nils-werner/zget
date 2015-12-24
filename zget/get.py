#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, \
    unicode_literals
import os
import sys
import time
import socket
try:
    import urllib.request as urllib
    import urllib.parse as urlparse
except ImportError:
    import urllib
    import urlparse
import hashlib
import logging

from zeroconf import ServiceBrowser, Zeroconf

from . import utils
from .utils import _
import argparse

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
            utils.logger.info(_("Peer found. Downloading..."))
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
        help=_("Verbose mode. Multiple -v options increase the verbosity")
    )
    parser.add_argument(
        '--quiet', '-q',
        action='count', default=0,
        help=_("Quiet mode. Hides progess bar")
    )
    parser.add_argument(
        '--timeout', '-t',
        type=int, metavar=_("SECONDS"),
        help=_("Set timeout after which program aborts transfer")
    )
    parser.add_argument(
        '--version', '-V',
        action='version',
        version='%%(prog)s %s' % utils.__version__
    )
    parser.add_argument(
        'filename', metavar=_("filename"),
        nargs='?',
        help=_("The filename to look for on the network")
    )
    parser.add_argument(
        'output', metavar=_("output"),
        nargs='?',
        help=_("The local filename to save to")
    )
    args = parser.parse_args(inargs)

    utils.enable_logger(args.verbose)

    if args.filename is None:
        args.filename = utils.generate_alias()
        if not args.quiet:
            print(
                _("Upload a file using `zput <filename> %s`") % (args.filename)
            )
    else:
        if not args.quiet:
            print(_(
                "Upload a file using `zput %(f)s` or `zput <filename> %(f)s`"
            ) % {'f': args.filename})

    if args.output is not None:
        progname = args.output
    else:
        progname = args.filename

    try:
        with utils.Progresshook(progname) as progress:
            get(
                args.filename,
                args.output,
                reporthook=progress if args.quiet == 0 else None,
                timeout=args.timeout
            )
    except Exception as e:
        if args.verbose:
            raise
        utils.logger.error(str(e))
        sys.exit(1)


def get(
    filename,
    output=None,
    reporthook=None,
    timeout=None
):
    """Receive and save a file using the zget protocol.

    Parameters
    ----------
    filename : string
        The filename to be transferred
    output : string
        The filename to save to. Optional.
    reporthook : callable
        A hook that will be called during transfer. Handy for watching the
        transfer. See :code:`urllib.urlretrieve` for callback parameters.
        Optional.
    timeout : int
        Seconds to wait until process is aborted. A running transfer is not
        aborted even when timeout was hit. Optional.

    Raises
    -------
    TimeoutException
        When a timeout occurred.

    """
    basename = os.path.basename(filename)
    filehash = hashlib.sha1(basename.encode('utf-8')).hexdigest()

    zeroconf = Zeroconf()
    listener = ServiceListener()
    listener.filehash = filehash

    utils.logger.debug(_("Looking for %s._zget._http._tcp.local.") % filehash)

    browser = ServiceBrowser(zeroconf, "_zget._http._tcp.local.", listener)

    start_time = time.time()
    try:
        while listener.address is None:
            time.sleep(0.5)
            if (
                timeout is not None and
                time.time() - start_time > timeout
            ):
                zeroconf.close()
                raise utils.TimeoutException()

        utils.logger.debug(
            _("Downloading from %(a)s:%(p)d") %
            {'a': listener.address, 'p': listener.port}
        )
        url = "http://" + listener.address + ":" + str(listener.port) + "/" + \
              urllib.pathname2url(filename)

        utils.urlretrieve(
            url, output,
            reporthook=reporthook
        )
    except KeyboardInterrupt:
        pass
    utils.logger.info(_("Done."))
    zeroconf.close()

if __name__ == '__main__':
    cli(sys.argv[1:])
