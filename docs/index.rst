Welcome to zget's documentation!
================================

Zget is a simple, Zeroconf-based, peer to peer file transfer utility, for situations where you and your peer are sitting next to each other and want to transfer a file quickly (and can shout the filename across the room).

Files and peers are recognized by the filename they want to transfer, not by their hostnames or IPs.

zget uses the fact that the filename is known to both parties as a basic authentication feature: The sender only advertises the sha1 hash of the filename on the network. Since the receiver must also know the filename, it can look for the sha1 using zeroconf.

If a match was found, a simple HTTP request is made: For transferring the file the actual filename is then requested from the sender. If this filename wasn't correct, the process is aborted.

The only third party dependency is `zeroconf <https://pypi.python.org/pypi/zeroconf>`_, a platform independent pure-Python Zeroconf implementation.

.. code:: bash

    $ zput file.zip

on the sender and

.. code:: bash

    $ zget file.zip

on the receiver.

Done.

Contents:

.. toctree::
   :maxdepth: 2

   commandline
   modules
   license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
