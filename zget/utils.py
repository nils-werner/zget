import sys
import os
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
