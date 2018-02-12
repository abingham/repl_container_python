import asyncio
import os
import pty
import signal

from aiohttp import web


repls = {}
logs = {}
queues = {}

app = web.Application()
loop = asyncio.get_event_loop()


async def kill_all_repls(app):
    global repls
    for proc, fd, queue in repls.values():
        proc.kill()
    repls = {}

app.on_shutdown.append(kill_all_repls)


class AsyncPTY:
    def __init__(self, *cmd, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()

        self.master, self.slave = pty.openpty()

        self.queue = asyncio.Queue()
        self.proc = None

        # Enqueue all process output for later reading
        loop.add_reader(
            self.master,
            lambda: self.queue.put_nowait(
                os.read(self.master, 1024)))

    def read(self):
        return self.queue.get()

    def write(self, data):
        return os.write(self.master, data)

    @property
    def pid(self):
        return self.proc.pid

    def kill(self):
        os.kill(self.pid, signal.SIGKILL)

    @staticmethod
    async def create(*cmd, loop=None):
        apty = AsyncPTY(cmd, loop)

        assert apty.proc is None

        # TODO: Perhaps this is overkill. Do we really need to create the
        # process asynchronously? If not, then this factory function isn't
        # necessary.
        apty.proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=apty.slave,
            stdout=apty.slave,
            stderr=apty.slave)

        return apty


async def index(request):
    with open('src/static/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


async def create_repl(request):
    """Start a new REPL accessed through a PTY.
    """
    proc = await AsyncPTY.create('python')
    repls[proc.pid] = proc
    return web.Response(
        text=str(proc.pid))


async def process_repl_output(ws, proc):
    while True:
        data = await proc.read()
        ws.send_str(data.decode('utf-8'))


async def websocket_handler(request):
    pid = int(request.match_info['pid'])

    socket = web.WebSocketResponse()
    await socket.prepare(request)

    proc = repls[pid]

    loop.create_task(
        process_repl_output(socket, proc))

    async for msg in socket:
        proc.write(msg.data.encode('utf-8'))

    await socket.close()
    return socket


app.router.add_static('/static', 'src/static')
app.router.add_get('/', index)
app.router.add_post('/repls', create_repl)
app.router.add_route('GET', '/repls/{pid}', websocket_handler)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--auto-reload', action='store_true',
                        help='run in auto-reload mode')
    args = parser.parse_args()

    if args.auto_reload:
        import aiohttp_autoreload
        aiohttp_autoreload.start()

    web.run_app(app)
