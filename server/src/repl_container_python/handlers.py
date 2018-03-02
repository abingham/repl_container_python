import logging
import pathlib
import tempfile

import sanic.exceptions
import sanic.response

from .async_pty_process import AsyncPTYProcess
from . import utils

log = logging.getLogger()


class ReplManager:
    def __init__(self, websockets, loop, file_data):
        self.websockets = websockets
        self.tempdir = tempfile.TemporaryDirectory()

        tempdir_path = pathlib.Path(self.tempdir.name)
        utils.write_source_files(tempdir_path, file_data)
        utils.run_setup_py(tempdir_path)

        self.process = AsyncPTYProcess(
            'python3',
            loop=loop,
            cwd=self.tempdir.name)
        self.task = loop.create_task(self._read_from_repl())

    def close(self):
        self.task.cancel()
        self.process.kill()

        self.task = None
        self.process = None

    async def _read_from_repl(self):
        while self.process is not None:
            data = await self.process.read()
            log.info('from repl: %s', data)
            decoded = data.decode('utf-8')
            for ws in self.websockets:
                await ws.send(decoded)

    def write(self, msg):
        self.process.write(msg.encode('utf-8'))


class Handlers:
    """Handlers for various routes in the app, plus attributes for tracking the
    REPL process.
    """

    def __init__(self):
        self.websockets = set()
        self.repl_mgr = None

    def close(self):
        if self.repl_mgr is not None:
            log.info('destroying REPL')
            self.repl_mgr.close()
            self.repl_mgr = None

        assert self.repl_mgr is None

    async def create_repl_handler(self, request):
        log.info("wama lama ding dong")
        if self.repl_mgr is not None:
            log.info('request to create REPL while one already exists')
            return sanic.response.HTTPResponse(status=409)

        log.info('creating REPL')

        self.repl_mgr = ReplManager(self.websockets,
                                    request.app.loop,
                                    request.json)

        # TODO: Detect and respond to failures in creating the ReplManager

        return sanic.response.HTTPResponse(status=201)  # created

    async def delete_repl_handler(self, request):
        # If there's not extant REPL, slap 'em with a 404
        if self.repl_mgr is None:
            return sanic.response.HTTPResponse(status=404)

        self.close()

        # TODO: Detect and respond to failures in closure

        return sanic.response.HTTPResponse(status=200)  # OK

    async def websocket_handler(self, request, ws):
        """Create a new websocket and connect it's input and output to the subprocess
        with the specified PID.
        """

        log.info('initiating websocket')

        self.websockets.add(ws)

        try:
            # Write all websocket input into the subprocess.
            async for msg in ws:
                log.info('from socket: %s', msg)
                if self.repl_mgr:
                    self.repl_mgr.write(msg)
        finally:
            log.info('terminating websocket')

            self.websockets.remove(ws)
