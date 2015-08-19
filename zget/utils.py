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


class TimeoutException(Exception):
    message = "Timeout."


class Progresshook(object):
    pbar = None

    def __call__(self, count, blocksize, totalsize):

        # In case we don't know the size of the file. zget < 0.8 did not
        # report file sizes via HTTP.
        if totalsize <= 0:
            # The callback is called too rapidly, which makes the BouncingBar
            # bounce too quickly and look stupid. By lowering the count number
            # (which has no real meaning in this case anyways) the bar looks
            # nicer
            count /= 2 ** 8
            if self.pbar is None:
                self.pbar = progressbar.ProgressBar(
                    widgets=[
                        progressbar.BouncingBar(),
                    ],
                    maxval=progressbar.UnknownLength
                )
                self.pbar.start()

            self.pbar.update(count)

        # zget >= 0.8 does report file sizes and enables percentage and ETA
        # display.
        else:
            if self.pbar is None:
                self.pbar = progressbar.ProgressBar(
                    widgets=[
                        progressbar.Percentage(),
                        progressbar.Bar(),
                        progressbar.ETA()
                    ],
                    # Make sure we have at least 1, otherwise the bar does
                    # not show 100% for small transfers
                    maxval=max(totalsize // blocksize, 1)
                )
                self.pbar.start()

            # Make sure we have at least 1, otherwise the bar does not show
            # 100% for small transfers
            self.pbar.update(max(min(count, totalsize // blocksize), 1))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if self.pbar is not None:
            self.pbar.finish()


def config():
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


def ip_addr(interface=None):
    """
    Get IP address from default gateway interface.

    Some OSes return 127.0.0.1 when using
    socket.gethostbyname(socket.gethostname()),
    so we're attempting to get a kind of valid hostname here.
    """
    try:
        if interface is None:
            interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
    except KeyError:
        raise ValueError("You have selected an invalid interface")
