import asyncio
import os
import pty

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


async def index(request):
    with open('src/static/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


async def create_repl(request):
    """Start a new REPL accessed through a PTY.
    """
    master, slave = pty.openpty()

    queue = asyncio.Queue()
    proc = await asyncio.create_subprocess_exec(
        'python',
        stdin=slave,
        stdout=slave,
        stderr=slave)
    loop.add_reader(master, lambda: queue.put_nowait(os.read(master, 1024)))

    repls[proc.pid] = (proc, master, queue)
    return web.Response(
        text=str(proc.pid))


async def process_repl_output(ws, queue):
    while True:
        data = await queue.get()
        print('repl output:', data)
        ws.send_str(data.decode('utf-8'))


async def websocket_handler(request):
    pid = int(request.match_info['pid'])

    socket = web.WebSocketResponse()
    await socket.prepare(request)

    proc, repl_fd, queue = repls[pid]

    loop.create_task(
        process_repl_output(socket, queue))

    async for msg in socket:
        os.write(repl_fd, msg.data.encode('utf-8'))

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
