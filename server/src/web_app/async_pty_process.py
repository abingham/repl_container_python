import asyncio
import os
import pty
import signal
import subprocess


class AsyncPTYProcess:
    """Runs a subprocess behind a PTY, providing async reading.
    """
    def __init__(self, *cmd, loop=None, cwd=None):
        if loop is None:
            loop = asyncio.get_event_loop()

        self.master, self.slave = pty.openpty()

        self.queue = asyncio.Queue()
        self.proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdin=self.slave,
            stdout=self.slave,
            stderr=self.slave)

        # Enqueue all process output for later reading
        loop.add_reader(
            self.master,
            lambda: self.queue.put_nowait(
                os.read(self.master, 1024)))

    def read(self):
        """Read the next chunk of output from the subprocess's stdout.

        This returns an awaitable coroutine.
        """
        return self.queue.get()

    def write(self, data):
        """Write `data` to the subprocess's stdin.
        """
        return os.write(self.master, data)

    @property
    def pid(self):
        """The process ID of the subprocess.
        """
        return self.proc.pid

    def kill(self):
        """Kill the subprocess.
        """
        os.kill(self.pid, signal.SIGKILL)
