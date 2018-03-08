import logging
import pathlib
import tempfile

from .async_pty_process import AsyncPTYProcess
from . import utils

log = logging.getLogger()


class ReplManager:
    def __init__(self, loop, file_data):
        """
        Raises:
            OSError: If there are problems starting the process.
        """
        self.websockets = set()
        self.tempdir = tempfile.TemporaryDirectory()

        tempdir_path = pathlib.Path(self.tempdir.name)
        utils.write_source_files(tempdir_path, file_data)
        utils.run_setup_py(tempdir_path)

        self.process = AsyncPTYProcess(
            'python3',
            loop=loop,
            cwd=self.tempdir.name)
        self.read_repl_task = loop.create_task(self._read_from_repl())

    def close(self):
        self.websockets.clear()
        self.read_repl_task.cancel()
        self.process.kill()

        self.read_repl_task = None
        self.process = None

    async def _read_from_repl(self):
        while self.process is not None:
            data = await self.process.read()
            log.info('from repl: %s', data)
            decoded = data.decode('utf-8')
            for ws in self.websockets:
                await ws.send(decoded)

    async def process_websocket(self, ws):
        self.websockets.add(ws)

        try:
            # Write all websocket input into the subprocess.
            async for msg in ws:
                log.info('from socket: %s', msg)
                self.write(msg)
        finally:
            self.websockets.remove(ws)

    def write(self, msg):
        self.process.write(msg.encode('utf-8'))
