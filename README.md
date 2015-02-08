Gynt
====

A simple peer to peer file transfer utility, for situations where you and your peer are sitting next to each other and want to transfer a file quickly (and can shout the filename across the room).

Files and peers are recognized by the filename they want to transfer, not by their hostnames or IPs.

Gynt uses the fact that the filename is known to both parties as a security feature: The sender only advertises the sha1 sum of the filename. Since the receiver must also know the filename, that sha1 is being looked for using zeroconf.

For transferring the file the actual filename is then sent to the sender. If this filename wasn't correct, the process is aborted.

Installation
------------

    $ pip install gynt

Usage
-----

On the sender, do:

    $ pynt my_holiday_pictures.zip

and on the receiver side

    $ gynt my_holiday_pictures.zip

Boom. Done.
