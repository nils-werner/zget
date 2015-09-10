zget
====

[![Build Status](https://travis-ci.org/nils-werner/zget.svg?branch=master)](https://travis-ci.org/nils-werner/zget)
[![Docs Status](https://readthedocs.org/projects/zget/badge/?version=stable)](https://zget.readthedocs.org/en/stable/)
[![Latest Version](https://img.shields.io/pypi/v/zget.svg)](https://pypi.python.org/pypi/zget/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/zget.svg)](https://pypi.python.org/pypi/zget/)
[![License](https://img.shields.io/pypi/l/zget.svg)](https://pypi.python.org/pypi/zget/)

A simple, Zeroconf-based, peer to peer file transfer utility, for situations where you and your peer are sitting next to each other and want to transfer a file quickly (and can shout the filename across the room).

Files and peers are recognized by the filename they want to transfer, not by their hostnames or IPs.

zget uses the fact that the filename is known to both parties as a basic authentication feature: The sender only advertises the sha1 hash of the filename on the network. Since the receiver must also know the filename, it can look for the sha1 using zeroconf.

If a match was found, a simple HTTP request is made: For transferring the file the actual filename is then requested from the sender. If this filename wasn't correct, the process is aborted.

The only third party dependency is [zeroconf](https://pypi.python.org/pypi/zeroconf), a platform independent pure-Python Zeroconf implementation.

Installation
------------

    $ pip install --user zget

If `zget` cannot be found afterwards you may also need to add

    export PATH=$HOME/.local/bin:$PATH

to your `.bashrc`.

Usage
-----

zget works both ways:

 - `zput` for sharing a file
 - `zget` for receiving


### Sharing

To share some nice pictures do:

    $ zput my_holiday_pictures.zip

then shout

> Hey Tom, I am zgetting you my_holiday_pictures.zip!

Tom will then do

    $ zget my_holiday_pictures.zip

Done.


### Receiving

You want to have some very important annual reports from Marcy:

    $ zget annual_reports.xlsx

then shout

> Hey Marcy, can you zget me annual_reports.xlsx?

Marcy then does

    $ zput annual_reports.xlsx

Boom. Done.


### Options

You may inspect the available options using

    $ zput -h

or

    $ zget -h


Configuration
-------------

By default zget uses a random open port and the sending party must be able to
accept incoming connections. This may be a problem when you have
restrictive firewall settings or multiple network cards.

You may create a config file

 - `~/.zget.cfg` on Linux/OSX
 - `%APPDATA%/zget/zget.ini` on Windows

to permanently set the port number and/or interface zget uses, e.g.

    [DEFAULT]
    port = 8080
    interface = eth0

Note that port numbers below 1024 may require root permissions to be opened.


Python Interface
----------------

As of zget 0.8, there exists a Python interface for sending and receiving
files as function calls. E.g.:

For sending:

    import zget
    zget.put("filename", port=2200)

and for receiving:

    import zget
    zget.get("filename", "filename_to_save_to")

For more information please see the [API reference](https://zget.readthedocs.org/).
