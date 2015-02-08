Gynt
====

A simple peer to peer file transfer utility, for situations where you and your peer are sitting next to each other and want to transfer a file quickly (and can shout the filename across the room).

Files and peers are recognized by the filename they want to transfer, not by their hostnames or IPs.

Gynt uses the fact that the filename is known to both parties as a security feature: The sender only advertises the sha1 sum of the filename on the network. Since the receiver must also know the filename, it can look for the sha1 using zeroconf.

If a match was found, a simple HTTP request is made: For transferring the file the actual filename is then requested from the sender. If this filename wasn't correct, the process is aborted.

Installation
------------

    $ pip install gynt

Usage
-----

Gynt works both ways:

 - `pynt` for sharing a file
 - `gynt` for receiving


### Sharing

To share some nice pictures do:

    $ pynt my_holiday_pictures.zip

then shout

> Hey Tom, I am gynting you my_holiday_pictures.zip!

Tom will then do

    $ gynt my_holiday_pictures.zip

Done.


### Receiving

You want to have some very important annual reports from Marcy:

    $ gynt annual_reports.xlsx

then shout

> Hey Marcy, can you gynt me annual_reports.xlsx?

Marcy then does

    $ pynt annual_reports.xlsx

Boom. Done.
