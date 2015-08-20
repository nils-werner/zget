Command Line Interface
======================

After installing, this toolkit provides a two command line utilities

.. code:: bash

    $ zget

and

.. code:: bash

    $ zput

Upload
------

:code:`zput` knows a few parameters that allow you to set the behaviour to
your needs:

 - :code:`-a ADDRESS` lets you manually set the IP address to broadcast and bind to
   (e.g. :code:`192.168.0.1`)
 - :code:`-i INTERFACE` lets you manually select the network card to broadcast on
   (e.g. :code:`eth0`)
 - :code:`-p PORT` lets you manually select the port to open.
   (e.g. :code:`8080`)
 - :code:`-v` (one or more) lets you increase verbosity, to debug failing connections.
 - :code:`-q` lets you hide the progress bar, for batch processing.
 - :code:`-t SECONDS` lets you set a timeout after which the transfer is aborted and
   a non-zero exit value is returned
 
Download
------

:code:`zget` knows a few parameters that allow you to set the behaviour to
your needs:

 - :code:`-v` (one or more) lets you increase verbosity, to debug failing connections.
 - :code:`-q` lets you hide the progress bar, for batch processing.
 - :code:`-t SECONDS` lets you set a timeout after which the transfer is aborted and
   a non-zero exit value is returned

.. note:: Each unit provides a help-switch :code:`-h` to investigate its parameters.
