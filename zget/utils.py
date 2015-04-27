import os
import ConfigParser


def config():
    config = ConfigParser.SafeConfigParser(
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
