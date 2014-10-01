tmbackup: remote backups of a Time Machine image
================================================

``tmbackup`` performs remote backups of your Time Machine image, including deletion of 
outdated snapshots. A more complete description is available on 
`cabbages-and-kings.net <https://www.cabbages-and-kings.net/2014/10/01/backup_of_a_time_machine_bundle_part_ii.html>`_.

Installation
------------

Apart from the files in this project, you'll need:

* Python
* rsync
* `sparsebundlefs <https://github.com/torarnv/sparsebundlefs>`_
* `tmfs <https://github.com/abique/tmfs>`_
* a Time Machine image and somewhere to store it remotely

Usage
-----

Basic usage is:

.. code-block:: bash

    tmbackup /somewhere/computer.sparsebundle/ user@backup.example.com:/home/user

You can also pass ``rsync`` options, e.g. authentication information:

.. code-block:: bash

    tmbackup --rsync-args="--password-file=/somewhere/backup.passwd" /somewhere/computer.sparsebundle/ rsync://user@backup.example.com/home/user
