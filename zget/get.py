#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, \
    unicode_literals
import sys
import socket
import hashlib
import argparse

try:
    from queue import Queue, Empty  # Py3
except ImportError:
    from Queue import Queue, Empty  # Py2

from zeroconf import ServiceBrowser, Zeroconf

from . import utils

__all__ = ["get"]


class ServiceListener(object):
    """
    Custom zeroconf listener that is trying to find the service we're looking
    for.

    """
    def __init__(self, token, filehash=None):
        self.token = token
        self.filehash = filehash
        self.queue = Queue()

    def remove_service(*args):
        pass

    def add_service(self, zeroconf, type, name):
        if name == self.token + "._zget._http._tcp.local.":
            mechanism = 'token'
        elif name == self.filehash + "._zget._http._tcp.local.":
            mechanism = 'filehash'
        else:
            # Someone else's transfer - ignore it
            return

        utils.logger.info("Peer found. Downloading...")
        info = zeroconf.get_service_info(type, name)
        if info:
            address = socket.inet_ntoa(info.address)
            self.queue.put((address, info.port, mechanism))


def cli(inargs=None):
    """
    Commandline interface for receiving files

    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--verbose', '-v',
        action='count', default=0,
        help="Verbose mode. Multiple -v options increase the verbosity"
    )
    parser.add_argument(
        '--quiet', '-q',
        action='count', default=0,
        help="Quiet mode. Hides progess bar"
    )
    parser.add_argument(
        '--timeout', '-t',
        type=int, metavar="SECONDS",
        help="Set timeout after which program aborts transfer"
    )
    parser.add_argument(
        '--version', '-V',
        action='version',
        version='%%(prog)s %s' % utils.__version__
    )
    parser.add_argument(
        'token', nargs='?',
        help=("The token to look for on the network, if zput was already"
              "started")
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
                args.token,
                args.output,
                reporthook=progress if args.quiet == 0 else None,
                timeout=args.timeout
            )
    except Exception as e:
        if args.verbose:
            raise
        utils.logger.error("%s", e)
        sys.exit(1)


def get(
    token_or_filename=None,
    output=None,
    reporthook=None,
    timeout=None
):
    """Receive and save a file using the zget protocol.

    Parameters
    ----------
    token_or_filename : string
        The token from zput, or the filename to be transferred. If not given,
        a random token will be generated and printed to use with zput.
        Optional.
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
    broadcast_token, secret_token = utils.prepare_token(token_or_filename)
    utils.logger.debug('Broadcast token: %s', broadcast_token)
    utils.logger.debug('Secret token: %s', secret_token)

    zeroconf = Zeroconf()
    if token_or_filename is not None:
        filehash = hashlib.sha1(token_or_filename.encode('utf-8')).hexdigest()
    else:
        filehash = None
    listener = ServiceListener(broadcast_token, filehash)

    utils.logger.debug("Looking for " + broadcast_token +
                       "._zget._http._tcp.local.")

    browser = ServiceBrowser(zeroconf, "_zget._http._tcp.local.", listener)

    if token_or_filename is None:
        print('Ready to receive a file.')
        print("Ask your friend to 'zput <filename> %s%s'"
              % (broadcast_token, secret_token))

    try:
        try:
            address, port, mechanism = listener.queue.get(timeout=timeout)
        except Empty:
            zeroconf.close()
            raise utils.TimeoutException()

        utils.logger.debug(
            "Downloading from %s:%d" % (address, port)
        )
        if mechanism == 'token':
            path = secret_token
        else:  # mechanism == 'filehash'
            path = token_or_filename
        url = "http://" + address + ":" + str(port) + "/" + path

        utils.urlretrieve(
            url, output,
            reporthook=reporthook
        )
    except KeyboardInterrupt:
        pass
    utils.logger.info("Done.")
    zeroconf.close()

if __name__ == '__main__':
    cli(sys.argv[1:])
