import sys
import os
import netifaces
import logging
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

logger = logging.getLogger('zget')


def config():
    config = configparser.SafeConfigParser(
        defaults={
            'port': '0',
        },
        allow_no_value=True
    )
    config.read([
        '.zget.cfg',
        os.path.expanduser('~/.zget.cfg'),
        os.path.join(os.getenv('APPDATA', ''), 'zget', 'zget.ini'),
    ])

    return config


def enable_logger(level=logging.INFO):
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
