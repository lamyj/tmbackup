import os
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
