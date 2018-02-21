import logging

from aiohttp import web

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
        return web.Response(
            text=str(self.process.pid))

    async def delete_repl_handler(self, request):
        log.info('destroying REPL')
        self.kill()
        return web.Response()

    async def websocket_handler(self, request):
        """Create a new websocket and connect it's input and output to the subprocess
        with the specified PID.
        """

        # TODO: What if process hasn't been started? Probably just return a 404
        # or something. Though we could also start one.

        log.info('initiating websocket')

        socket = web.WebSocketResponse()
        await socket.prepare(request)

        async def process_repl_output():
            """Pipe output from `proc` into the websocket `ws`.
            """
            while True:
                data = await self.process.read()
                log.info('from repl: %s', data)
                await socket.send_str(data.decode('utf-8'))

        # Arrange for the process output to be written to the websocket.
        repl_output_task = request.app.loop.create_task(process_repl_output())

        # Write all websocket input into the subprocess.
        async for msg in socket:
            log.info('from socket: %s', msg.data)
            self.process.write(msg.data.encode('utf-8'))

        repl_output_task.cancel()
        await socket.close()

        log.info('terminating websocket')

        return socket
