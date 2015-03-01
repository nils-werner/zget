#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, \
    unicode_literals
import sys
import time
import socket
try:
    import urllib.request as urllib
except ImportError:
    import urllib
import hashlib
import argparse

from zeroconf import ServiceBrowser, Zeroconf

filename = ""
filehash = ""
output = ""
downloaded = False


class ServiceListener(object):
    def remove_service(*args):
        pass

    def add_service(self, zeroconf, type, name):
        global downloaded, filename, filehash, output
        if name == filehash + "._zget._http._tcp.local.":
            print("Peer found. Downloading...")
            info = zeroconf.get_service_info(type, name)
            if info:
                address = socket.inet_ntoa(info.address)
                port = info.port
                url = "http://" + address + ":" + str(port) + "/" + filename
                urllib.urlretrieve(url, output)
                downloaded = True


def get(inargs=None):
    global downloaded, filename, filehash, output

    parser = argparse.ArgumentParser()

    parser.add_argument(
        'filename',
        help="The filename to look for on the network"
    )
    parser.add_argument(
        'output',
        nargs='?',
        help="The local filename to save to"
    )
    args = parser.parse_args(inargs)

    filename = args.filename
    filehash = hashlib.sha1(filename.encode('utf-8')).hexdigest()
    downloaded = False
    if args.output is not None:
        output = args.output
    else:
        output = filename

    zeroconf = Zeroconf()
    listener = ServiceListener()
    browser = ServiceBrowser(zeroconf, "_zget._http._tcp.local.", listener)

    while not downloaded:
        time.sleep(0.5)
    print("Done.")
    zeroconf.close()


if __name__ == '__main__':
    get(sys.argv[1:])
