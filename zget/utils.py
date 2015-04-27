import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser


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
