#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, \
    unicode_literals
import os
import sys
import time
import base64
import socket
import six.moves.urllib as urllib
import getpass
import hashlib
import logging

from zeroconf import ServiceInfo, Zeroconf
from six.moves.BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from . import utils
from . import crypto
from .utils import _
import argparse

__all__ = ["put"]


def validate_address(address):
    """ Validate IP address
    """
    try:
        socket.inet_aton(address)
        return address
    except socket.error:
        raise argparse.ArgumentTypeError(
            _("%s is not a valid IP address") % address
        )


class StateHTTPServer(HTTPServer):
    """
    HTTP Server that knows a certain filename and can be set to remember if
    that file has been transferred using :class:`FileHandler`
    """
    downloaded = False
    filename = ""
    allowed_basenames = []
    reporthook = None


class FileHandler(BaseHTTPRequestHandler):
    """
    Custom HTTP upload handler that allows one single filename to be requested.

    """

    def do_GET(self):
        if self.path in map(
            lambda x: urllib.request.pathname2url(os.path.join('/', x)),
            self.server.allowed_basenames
        ):
            key_b = base64.urlsafe_b64encode(
                self.server.ciphersuite.start()
            )
            try:
                self.server.ciphersuite.finish(
                    base64.urlsafe_b64decode(self.headers['key-exchange-a'])
                )
            except KeyError:
                pass

            utils.logger.info(_("Peer found. Uploading..."))
            full_path = os.path.join(os.curdir, self.server.filename)
            with open(full_path, 'rb') as fh:
                maxsize = os.path.getsize(full_path)
                self.send_response(200)
                self.send_header('Content-type', 'application/octet-stream')
                self.send_header('key-exchange-b', key_b.decode("ascii"))
                self.send_header(
                    'Content-disposition',
                    'inline; filename="%s"' % os.path.basename(
                        self.server.filename
                    )
                )
                self.send_header(
                    'Content-length',
                    self.server.ciphersuite.size(maxsize)
                )
                self.end_headers()

                for i, data in enumerate(
                    self.server.ciphersuite(utils.iter_content(fh))
                ):
                    self.wfile.write(data)
                    if self.server.reporthook is not None:
                        self.server.reporthook(i, 1024 * 8, maxsize)
            self.server.downloaded = True

        else:
            self.send_response(404)
            self.end_headers()
            raise RuntimeError(_("Invalid request received. Aborting."))

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
        '--port', '-P',
        type=int, nargs='?', metavar=_("PORT"),
        help=_("The port to share the file on")
    )
    parser.add_argument(
        '--address', '-a', nargs='?',
        type=validate_address, metavar=_("ADDRESS"),
        help=_("The address to share the file on")
    )
    parser.add_argument(
        '--interface', '-i', nargs='?', metavar=_("INTERFACE"),
        help=_("The interface to share the file on")
    )
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
        '--password', '-p',
        nargs='?',
        metavar=_("PASSWORD"),
        help=_("Password for transfer encryption")
    )
    parser.add_argument(
        '--bypass-encryption',
        action='store_true',
        help=_("Bypass transfer encryption, for legacy clients. DANGEROUS!")
    )
    parser.add_argument(
        '--version', '-V',
        action='version',
        version='%%(prog)s %s' % utils.__version__
    )
    parser.add_argument(
        'input', metavar=_("input"),
        help=_("The file to share on the network")
    )
    parser.add_argument(
        'output',
        nargs='?',
        help="The share alias on the network"
    )
    args = parser.parse_args(inargs)

    utils.enable_logger(args.verbose)

    if args.password is None and not args.bypass_encryption:
        args.password = getpass.getpass(
            (_("Password for '%s': ") % args.input).encode("utf-8", "ignore")
        )

    if not args.bypass_encryption:
        try:
            ciphersuite = crypto.aes_spake.encrypt(args.password)
        except ImportError:
            raise ImportError(_(
                "Could not load cipher suite. Did you install cryptography?"
            ))
    else:
        utils.logger.warn(
            _("WARNING: Encryption and authentication DISABLED!")
        )
        ciphersuite = crypto.bypass.encrypt()

    try:
        if not os.path.isfile(args.input):
            raise ValueError(
                _("File %s does not exist") % args.input
            )
        if args.interface and args.address:
            raise ValueError(
                _("You may only provide one of --address "
                  "or --interface")
            )

        if args.output is None:
            args.output = utils.generate_alias()

        if not args.quiet:
            print(_(
                "Download this file using `zget %(f)s` or `zget %(o)s`"
            ) % {'f': os.path.basename(args.input), 'o': args.output})

        with utils.Progresshook(args.input) as progress:
            put(
                args.input,
                output=args.output,
                interface=args.interface,
                address=args.address,
                port=args.port,
                reporthook=progress if args.quiet == 0 else None,
                timeout=args.timeout,
                ciphersuite=ciphersuite,
            )
    except Exception as e:
        if args.verbose:
            raise
        utils.logger.error(unicode(e))
        utils.logger.error(
            _("An Error occurred. For a full traceback try running zget "
              "again with enabled verbosity (-vvv).")
        )
        sys.exit(1)


def put(
    filename,
    output=None,
    interface=None,
    address=None,
    port=None,
    reporthook=None,
    timeout=None,
    ciphersuite=None,
):
    """Send a file using the zget protocol.

    Parameters
    ----------
    filename : string
        The filename to be transferred
    output : string
        The alias to share on the network. Optional. If empty, the input
        filename will be used.
    interface : string
        The network interface to use. Optional.
    address : string
        The network address to use. Optional.
    port : int
        The network port to use. Optional.
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
    if port is None:
        port = utils.config().getint('DEFAULT', 'port')

    if interface is None:
        interface = utils.config().get('DEFAULT', 'interface')

    if not 0 <= port <= 65535:
        raise ValueError(_("Port %d exceeds allowed range") % port)

    if ciphersuite is None:
        ciphersuite = crypto.bypass.encrypt()

    basename = os.path.basename(filename)

    filehashes = []
    filehashes.append(hashlib.sha1(basename.encode('utf-8')).hexdigest())
    if output is not None:
        filehashes.append(hashlib.sha1(output.encode('utf-8')).hexdigest())

    if interface is None:
        interface = utils.default_interface()

    if address is None:
        address = utils.ip_addr(interface)

    server = StateHTTPServer((address, port), FileHandler)
    server.timeout = timeout
    server.filename = filename
    server.allowed_basenames.append(basename)
    if output is not None:
        server.allowed_basenames.append(output)
    server.reporthook = reporthook
    server.ciphersuite = ciphersuite

    port = server.server_port

    utils.logger.debug(
        _("Using interface %s") % interface
    )

    utils.logger.debug(
        _("Listening on %(a)s:%(p)d \n"
          "you may change address using --address and "
          "port using --port") % {'a': address, 'p': port}
    )

    zeroconf = Zeroconf()

    infos = []
    for filehash in filehashes:
        utils.logger.debug(
            _("Broadcasting as %s._zget._http._tcp.local.") % filehash
        )
        infos.append(ServiceInfo(
            "_zget._http._tcp.local.",
            "%s._zget._http._tcp.local." % filehash,
            socket.inet_aton(address), port, 0, 0,
            {'path': None}
        ))

    try:
        for info in infos:
            zeroconf.register_service(info)
        server.handle_request()
    except KeyboardInterrupt:
        pass

    server.socket.close()
    for info in infos:
        zeroconf.unregister_service(info)
    zeroconf.close()

    if timeout is not None and not server.downloaded:
        raise utils.TimeoutException()
    else:
        utils.logger.info(_("Done."))

if __name__ == '__main__':
    cli(sys.argv[1:])
