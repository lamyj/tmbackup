import glob
import os
import re
import subprocess

def backup(source_root, computer, timestamp, previous_timestamp, destination_root, extra_args=None):
    """ Perform a remote rsync backup of a Time Machine snapshot.
    
        * ``source_root``: source directory of the mounted Time Machine volume
        * ``computer``: target computer backup inside the Time Machine Volume
        * ``timestamp``: timestamp to backup in the Time Machine format
        * ``previous_timestamp``: timestamp of the previous backup if ``--link-dest`` is
          to be used, ``None`` otherwise
        * ``destination_root``: destination URL of rsync. Computer and timestamp directories
          will be created inside.
        * ``extra_args``: extra arguments to be passed to rsync, specified as a list
    """
    
    backup_options = ["--archive", "--relative", "--delete", "--numeric-ids"]
    if extra_args:
        backup_options.extend(extra_args)
    
    command = ["rsync"]
    command.extend(backup_options)
    
    # If destination is remote, the "user@host:" must not be in link-dest option
    # id. for "rsync://" URLs
    if previous_timestamp:
        match = re.match(r"rsync://[^@]+@[^/]+/[^/]+(/.+)", destination_root)
        if match:
            previous_destination = os.path.join(match.group(1), computer, previous_timestamp)
        else:
            match = re.match(r"^[^@]+@[^:]+:(.*)", destination_root)
            if match:
                previous_destination = os.path.join(match.group(1), computer, previous_timestamp)
            else:
                previous_destination = os.path.join(destination_root, computer, previous_timestamp)
        command.extend(["--link-dest", previous_destination])    
    
    # Use implicit relative path with the "/./" pattern. cf. the ``--relative`` option in
    # the `rsync documentation <https://rsync.samba.org/ftp/rsync/rsync.html>`_.
    source = os.path.join(source_root, computer, timestamp, ".", "")
    destination = os.path.join(destination_root, computer, timestamp)
    command.extend([source, destination])
    
    subprocess.check_call(command)

def cleanup(source, computer, destination):
    """ Remove the snapshots on the destination URL that are missing from the source
        Time Machine volume.
        
        * ``source``: source directory of the mounted Time Machine volume
        * ``computer``: target computer backup inside the Time Machine Volume
        * ``destination``: destination URL of rsync. The computer directory must be 
          present at the URL.
    """
    
    pass
