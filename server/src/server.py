import asyncio
import logging
import os
import pty
import signal
import subprocess

from aiohttp import web

log = logging.getLogger()

app = web.Application()
loop = asyncio.get_event_loop()


class AsyncPTYProcess:
    """Runs a subprocess behind a PTY, providing async reading.
    """
    def __init__(self, *cmd, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()

        self.master, self.slave = pty.openpty()

        self.queue = asyncio.Queue()
        self.proc = subprocess.Popen(
            cmd,
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


class ReplHandler:
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


handler = ReplHandler()
app.router.add_post('/', handler.create_repl_handler)
app.router.add_delete('/', handler.delete_repl_handler)
app.router.add_get('/', handler.websocket_handler)


async def cleanup(app):
    handler.kill()

app.on_shutdown.append(cleanup)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default=None,
                        help='The port on which to serve HTTP.')
    parser.add_argument('--auto-reload', action='store_true',
                        help='run in auto-reload mode')
    parser.add_argument('-v', action='store_true',
                        help='enable verbose logging mode')
    parser.add_argument('-vv', action='store_true',
                        help='enable very verbose logging mode')
    args = parser.parse_args()

    level = logging.INFO if args.v else logging.WARNING
    level = logging.DEBUG if args.vv else level
    logging.basicConfig(level=level)

    if args.auto_reload:
        import aiohttp_autoreload
        aiohttp_autoreload.start()

    web.run_app(app, port=args.port)
