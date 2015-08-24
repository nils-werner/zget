import sys
import os
import netifaces
import logging
import progressbar
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

logger = logging.getLogger('zget')

__version__ = "0.9"


class TimeoutException(Exception):
    """ Exception raised when a timeout was hit.
    """
    message = "Timeout."


class Progresshook(object):
    """ Simple context manager that shows a progressbar for
    :code:`urllib.urlretrieve`-like callbacks.
    """
    filename = ""
    pbar = None

    def __call__(self, count, blocksize, totalsize):

        # In case we don't know the size of the file. zget < 0.9 did not
        # report file sizes via HTTP.
        if totalsize <= 0:
            if self.pbar is None:
                self.pbar = progressbar.ProgressBar(
                    widgets=[
                        self.filename,
                        ' ',
                        progressbar.BouncingBar(),
                        ' ',
                        progressbar.FileTransferSpeed(),
                    ],
                    maxval=progressbar.UnknownLength
                )
                self.pbar.start()

            # Make sure we have at least 1, otherwise the bar does not show
            # 100% for small transfers
            self.pbar.update(max(count * blocksize, 1))

        # zget >= 0.9 does report file sizes and enables percentage and ETA
        # display.
        else:
            if self.pbar is None:
                self.pbar = progressbar.ProgressBar(
                    widgets=[
                        self.filename,
                        ' ',
                        progressbar.Percentage(),
                        ' ',
                        progressbar.Bar(),
                        ' ',
                        progressbar.ETA(),
                        ' ',
                        progressbar.FileTransferSpeed(),
                    ],
                    # Make sure we have at least 1, otherwise the bar does
                    # not show 100% for small transfers
                    maxval=max(totalsize, 1)
                )
                self.pbar.start()

            # Make sure we have at least 1, otherwise the bar does not show
            # 100% for small transfers
            self.pbar.update(max(min(count * blocksize, totalsize), 1))

    def __init__(self, filename=""):
        self.filename = filename

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if self.pbar is not None:
            self.pbar.finish()


def config():
    """ Reads config values from zget.cfg or zget.ini
    """
    config = configparser.SafeConfigParser(
        defaults={
            'port': '0',
            'interface': None,
        },
        allow_no_value=True
    )
    config.read([
        '.zget.cfg',
        os.path.expanduser('~/.zget.cfg'),
        os.path.join(os.getenv('APPDATA', ''), 'zget', 'zget.ini'),
    ])

    return config


def enable_logger(verbosity=0):
    """ Set up and enable logger
    """
    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO
    else:
        level = logging.NOTSET

    formatter = logging.Formatter('%(message)s')
    logger.setLevel(level)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    ch.setFormatter(formatter)

    logger.addHandler(ch)


def default_interface():
    """ Get default gateway interface.

    Some OSes return 127.0.0.1 when using
    socket.gethostbyname(socket.gethostname()),
    so we're attempting to get a kind of valid hostname here.
    """
    return netifaces.gateways()['default'][netifaces.AF_INET][1]


def ip_addr(interface):
    """ Get IP address from interface.

    """
    try:
        return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
    except KeyError:
        raise ValueError("You have selected an invalid interface")
