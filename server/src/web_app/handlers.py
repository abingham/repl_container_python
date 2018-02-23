import logging

import sanic.response

from .async_pty_process import AsyncPTYProcess

log = logging.getLogger()


class Handlers:
    """Handlers for various routes in the app, plus attributes for tracking the
    REPL process.
    """

    def __init__(self):
        self.process = None

    def kill(self):
        if self.process is not None:
            self.process.kill()
            self.process = None

    async def create_repl_handler(self, request):
        log.info('creating REPL')
        self.kill()

        assert self.process is None

        self.process = AsyncPTYProcess('python3',
                                       loop=request.app.loop)

        return sanic.response.HTTPResponse(status=201)  # created

    async def delete_repl_handler(self, request):
        log.info('destroying REPL')
        self.kill()

        return sanic.response.HTTPResponse(status=200)  # OK

    async def websocket_handler(self, request, ws):
        """Create a new websocket and connect it's input and output to the subprocess
        with the specified PID.
        """

        # TODO: What if process hasn't been started? Probably just return a 404
        # or something. Though we could also start one.

        async def process_repl_output():
            """Pipe output from `proc` into the websocket `ws`.
            """
            while True:
                data = await self.process.read()
                log.info('from repl: %s', data)
                await ws.send(data.decode('utf-8'))

        # Arrange for the process output to be written to the websocket.
        repl_output_task = request.app.loop.create_task(process_repl_output())

        # Write all websocket input into the subprocess.
        async for msg in ws:
            log.info('from socket: %s', msg)
            self.process.write(msg.encode('utf-8'))

        repl_output_task.cancel()
