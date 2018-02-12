import asyncio
import functools
import json
import os

from aiohttp import web
import socketio


repls = {}
logs = {}
queues = {}

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)
loop = asyncio.get_event_loop()

async def kill_all_repls(app):
    # global repls
    # for transport, protocol in repls.values():
    #     if transport.get_returncode() is not None:
    #         try:
    #             print('killing repl:', transport.get_pid())
    #             transport.kill()
    #         except ProcessLookupError:
    #             pass
    # repls = {}
    pass

app.on_shutdown.append(kill_all_repls)


async def index(request):
    with open('src/static/index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


class ReplProtocol(asyncio.SubprocessProtocol):
    def __init__(self):
        super().__init__()
        self.queue = asyncio.Queue()

    def pipe_data_received(self, fd, data):
        self.queue.put_nowait(data)


async def create_repl(request):
    print('creating repl')
    transport, protocol = await loop.subprocess_exec(
        lambda: ReplProtocol(),
        'python', '-i', '-u',
        )

    # proc is a tuple of (transport, protocol)
    repls[transport.get_pid()] = (transport, protocol)
    return web.Response(
        text=str(transport.get_pid()))


async def process_repl_output(ws, queue):
    while True:
        data = await queue.get()
        print('repl output:', data)
        data = data.replace(b'\n', b'\r\n')
        ws.send_str(data.decode('utf-8'))

    # TODO: Need to properly handle ws shutdown? Or will that be handled
    # properly by the loop?


async def websocket_handler(request):
    pid = int(request.match_info['pid'])
    print('pid:', pid)

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    transport, protocol = repls[pid]

    loop.create_task(
        process_repl_output(ws, protocol.queue))

    async for msg in ws:
        data = msg.data.encode('utf-8').replace(b'\r', b'\n')
        ws.send_str(msg.data.replace('\r', '\r\n'))
        transport.get_pipe_transport(0).write(data)

    await ws.close()
    return ws


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
