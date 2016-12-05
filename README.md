zget
====

[![Build Status](https://travis-ci.org/nils-werner/zget.svg?branch=master)](https://travis-ci.org/nils-werner/zget)
[![Build status](https://ci.appveyor.com/api/projects/status/6yrye1hsvw5hvx4l?svg=true)](https://ci.appveyor.com/project/nils-werner/zget)
[![Docs Status](https://readthedocs.org/projects/zget/badge/?version=stable)](https://zget.readthedocs.org/en/stable/)
[![Latest Version](https://img.shields.io/pypi/v/zget.svg)](https://pypi.python.org/pypi/zget/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/zget.svg)](https://pypi.python.org/pypi/zget/)
[![License](https://img.shields.io/pypi/l/zget.svg)](https://pypi.python.org/pypi/zget/)

A simple, Zeroconf-based, peer to peer file transfer utility, for situations where you and your peer are sitting next to each other and want to transfer a file quickly (and can shout the filename across the room).

Files and peers are recognized by the filename they want to transfer, not by their hostnames or IPs.

zget uses the fact that the filename is known to both parties as a basic authentication feature: The sender only advertises the sha1 hash of the filename on the network. Since the receiver must also know the filename, it can look for the sha1 using zeroconf.

If a match was found, a simple HTTP request is made: For transferring the file the actual filename is then requested from the sender. If this filename wasn't correct, the process is aborted.

Installation
------------

    $ pip install zget

Usage
-----

zget works both ways:

 - `zput` for sharing a file
 - `zget` for receiving


### Sharing

To share some pictures do:

    $ zput my_holiday_pictures.zip

then shout

> Hey Tom, I am sending you my_holiday_pictures.zip!

Tom will then do

    $ zget my_holiday_pictures.zip

Done.


### Receiving

You want to have some very important data from Tom:

    $ zget annual_reports.xlsx

then shout

> Hey Tom, can you send me annual_reports.xlsx?

Tom then does

    $ zput annual_reports.xlsx

Boom. Done.


### Aliases

Alternatively, in case of really complicated filenames, you can use aliases or
have `zput` generate one for you:

    $ zput LICENSE
    Download this file using `zget LICENSE` or `zget C6P3`

Also `zget` can generate an alias so you can initiate the transfer without knowing
what file will be transferred.

    $ zget
    Upload a file using `zput <filename> YHKC`

As of version 0.10 `zget` will figure out the resulting filename from the transfer metadata, so you won't be stuck with a file `YHKC` on your computer.


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


Security Considerations
-----------------------

Neither Zeroconf nor HTTP, both technologies used in this tool, should be used
on untrusted networks (like public WiFi at a coffee shop).

Additonally, `zput` announces the filename and aliases as a simple unsalted
SHA-1 hash on the network. This means that a malicious party could trivially
intercept your transfers by simply generating a large enough number of hashes
and then accepting the transfer on behalf of the desired recipient.

In this case you should however notice the attack by the recipient never
receiving a file while the sender sees an upload happening.
