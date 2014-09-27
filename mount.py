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

    def __init__(self, image):
        self.image = image
    
    def __enter__(self):
        offset, size = self._get_offset_and_size()
        loop = subprocess.check_output(["losetup", "-f", self.image, 
            "--offset", offset, "--sizelimit", size, 
            "--show"])
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
    
    with mount(sparsebundle, "sparsebundlefs") as dmg:
        with losetup(os.path.join(dmg, "sparsebundle.dmg")) as loop:
            with mount(loop, "mount", "-t", "hfsplus") as disk:
                with mount(disk, "tmfs") as tmfs:
                    yield tmfs
