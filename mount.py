# Copyright 2014 Julien Lamy
#
# This file is part of tmbackup.
#
# tmbackup is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# tmbackup is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with tmbackup.  If not, see <http://www.gnu.org/licenses/>. 

import contextlib
import os
import re
import subprocess
import tempfile

class mount(object):
    """ Context manager mounting and un-mounting a filesystem on a temporary directory.
    
        >>> with mount("/dev/sdc1") as directory:
        ...     print os.listdir(directory)
    """

    def __init__(self, source, command="mount", *args):
        self.source = source
        self.command = command
        self.args = args

    def __enter__(self):
        """ Create a temporary directory and mount the filesystem there. Return the name
            of the directory.
        """
        
        self._directory = tempfile.mkdtemp()
        subprocess.check_output(
            [self.command, self.source]+list(self.args)+[self._directory])
        return self._directory

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Unmount the filesystem and remove the temporary directory.
        """
        
        subprocess.check_output(["umount", self._directory])
        os.rmdir(self._directory)

class losetup(object):
    """ Context manager mounting an un-mounting an image on a loop device. The size and
        offset of the partition in the image are automatically computed using parted.
    """

    def __init__(self, image, *args):
        self.image = image
        self.args = args
    
    def __enter__(self):
        offset, size = self._get_offset_and_size()
        loop = subprocess.check_output(["losetup", "-f", self.image, 
            "--offset", offset, "--sizelimit", size, 
            "--show"]+list(self.args))
        self.loop = loop.strip()
        return self.loop
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        subprocess.check_output(["losetup", "-d", self.loop])
    
    def _get_offset_and_size(self):
        offset, size = None, None
        data = subprocess.check_output(["parted", self.image, "unit", "B", "print"])
        for line in data.splitlines():
            match = re.search(r"(?P<start>\d+)B\s+\d+B\s+(?P<size>\d+)B\s+hfs\+", data)
            if match:
                offset, size = match.groups()
                break
        return offset, size

@contextlib.contextmanager
def mount_tmfs(sparsebundle):
    """ Context manager mounting a Time Machine image on a temporary directory. The
        temporary directory is deleted when the context manager exits.
    """
    
    with mount(sparsebundle, "sparsebundlefs", "-o", "ro") as dmg:
        with losetup(os.path.join(dmg, "sparsebundle.dmg"), "-r") as loop:
            with mount(loop, "mount", "-t", "hfsplus", "-o", "ro") as disk:
                with mount(disk, "tmfs", "-o", "ro") as tmfs:
                    yield tmfs
