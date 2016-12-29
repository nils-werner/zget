import sys
import os
import re
import errno
import base64
import random
import requests
import netifaces
import itertools
import gettext
import logging
import progressbar
from six.moves import configparser, range, zip_longest
import six.moves.urllib.parse as urlparse

t = gettext.translation(
    'zget',
    os.path.join(os.path.dirname(__file__), "locales"),
    fallback=True
)
try:
    _ = t.ugettext
except AttributeError:
    _ = t.gettext

logger = logging.getLogger('zget')

__version__ = "0.11.1"


class TimeoutException(Exception):
    """ Exception raised when a timeout was hit.
    """
    def __init__(self, msg=_("Timeout.")):
        super(TimeoutException, self).__init__(msg)


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
    try:
        return netifaces.gateways()['default'][netifaces.AF_INET][1]
    except KeyError:
        # Sometimes 'default' is empty but AF_INET exists alongside it
        return netifaces.gateways()[netifaces.AF_INET][0][1]


def ip_addr(interface):
    """ Get IP address from interface.

    """
    try:
        return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
    except KeyError:
        raise ValueError(_("You have selected an invalid interface"))


def unique_filename(filename, limit=999):
    if not os.path.exists(filename):
        return filename

    path, name = os.path.split(filename)
    name, ext = os.path.splitext(name)

    def make_filename(i):
        return os.path.join(path, '%s_%d%s' % (name, i, ext))

    for i in range(1, limit):
        unique_filename = make_filename(i)
        if not os.path.exists(unique_filename):
            return unique_filename

    try:
        raise FileExistsError()
    except NameError:
        raise IOError(errno.EEXIST)


def urlretrieve(
    url,
    output=None,
    reporthook=None,
    ciphersuite=None,
):
    from . import crypto

    if ciphersuite is None:
        ciphersuite = crypto.bypass.decrypt()

    r = requests.get(
        url, stream=True,
        headers={
            'key-exchange-a': base64.urlsafe_b64encode(ciphersuite.start())
        }
    )
    try:
        maxsize = int(r.headers['content-length'])
    except KeyError:
        maxsize = -1

    try:
        ciphersuite.finish(
            base64.urlsafe_b64decode(r.headers['key-exchange-b'])
        )
    except KeyError:
        pass

    if output is None:
        try:
            filename = re.findall(
                "filename=(.+)", r.headers['content-disposition']
            )[0].strip('\'"')
        except (IndexError, KeyError):
            filename = urlparse.unquote(
                os.path.basename(urlparse.urlparse(url).path)
            )
        filename = unique_filename(filename)
        reporthook.filename = filename
    else:
        filename = output

    try:
        with open(filename, 'wb') as f:
            for i, chunk in enumerate(
                ciphersuite(r.iter_content(chunk_size=1024 * 8))
            ):
                if chunk:
                    f.write(chunk)
                    if reporthook is not None:
                        reporthook(i, 1024 * 8, maxsize)
    except Exception as e:
        silentremove(filename)
        raise


def silentremove(filename):
    try:
        return os.remove(filename)
    except Exception:
        pass


def generate_alias(length=4):
    alphabet = '23456789ABCDEFGHJKMNPQRSTVWXYZ'
    return ''.join(random.choice(alphabet) for _ in range(length))


def iter_content(fh, chunksize=1024 * 8):
    while True:
        chunk = fh.read(chunksize)
        if chunk:
            yield chunk
        else:
            break


def minimum_chunksize(data, minlength=32):
    """
    Merge the last two elements of an iterable,
    if the last element is too short. This is needed for the decryptor to
    successfully read the entire signature of the HMAC.
    """
    for d, n in pairwise(data):
        if n is not None and len(n) < minlength:
            yield d + n
            raise StopIteration
        else:
            yield d


def pairwise(iterable):
    """
    Return pairs of an iterator

    s -> (s0,s1), (s1,s2), (s2, s3), ...
    """
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip_longest(a, b)
