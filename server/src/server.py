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


async def send_data(sid, lines):
    for line in lines:
        await sio.emit(
            'data',
            line.decode('utf-8'),
            room=sid,
            namespace='/repls')


# async def emit_messages():
#     while True:
#         sid, line = await message_queue.get()
#         print('emiting:', line)
#         await sio.emit(
#             'data',
#             line.decode('utf-8'),
#             room=sid,
#             namespace='/repls')

# loop.create_task(emit_messages())


class ReplProtocol(asyncio.SubprocessProtocol):
    def __init__(self):
        super().__init__()
        self.queue = asyncio.Queue()

    def pipe_data_received(self, fd, data):
        self.queue.put_nowait(data)

    def process_exited(self):
        print('process exited')


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

    while True:
        msg = await ws.receive()
        print('repl input:', msg)
        data = msg.data.encode('utf-8').replace(b'\r', b'\n')
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


# @app.route("/")
# def index():
#     return app.send_static_file('index.html')


# def repl_read(avatar_name, fd):
#     print('repl_read: {}'.format(avatar_name))
#     data = os.read(fd, 1024)

#     print('read:', data)

#     try:
#         socket = sockets[avatar_name]
#         socket.write(data)
#     except KeyError:
#         pass

#     assert avatar_name in logs
#     logs[avatar_name] += data

#     return data


# @socketio.on('connect')
# def handle_connect():
#     print('connect! {}'.format(request.args))

#     try:
#         avatar_name = request.args['avatar_name']
#         # cols = int(request.args['cols'])
#         # rows = int(request.args['rows'])
#     except KeyError:
#         # TODO: return appropriate HTTP error
#         raise
#     except ValueError:
#         # TODO: Raise appropriate HTTP error...int conversion has failed
#         raise

#     if avatar_name in repls:
#         old_repl = repls[avatar_name]
#         old_repl.kill()
#         print('Closed REPL:', old_repl.pid/sizee
#         del repls[avatar_name]
#         del logs[avatar_name]

#     repl = subprocess.Popen('python',
#                             stdin=subprocess.PIPE,
#                             stdout=subprocess.PIPE,
#                             stderr=subprocesss.STDOUT)
#     repls[avatar_name] = repl
# #         repl = pty.spawn(
# #             'python', [], {
# #                 name: 'xterm-color',  // Sets the TERM environment variable, so
# #                 // must be 'xterm' or 'xterm-color'
# #                 cols: cols || 80,
# #                 rows: rows || 24,
# #                 cwd: process.env.PWD,
# #                 env: process.env
# #             }),

#     print('Created Python REPL with PID:', repl.pid)
#     repls[avatar_name] = repl
#     logs[avatar_name] = ''

#     sel.register(repl.stdout, selectors.EVENT_READ, lambda data: repl_read(avatar_name, data))

#     # resp = jsonify({'repl_pid': repl.pid})
#     # resp.status_code = 201

#     # return resp


# @socketio.on('data')
# def handle_message(message):
#     print('received data: ', message)
#     repl = repls[message['avatar_name']]
#     repl.stdin.write(message['data'].encode('utf-8'))
#     repl.stdin.flush()


# @socketio.on('json')
# def handle_json(json):
#     print('received json: ' + str(json))

# # // Websocket for interacting with REPL
# # app.ws('/repls/:kata_id/:avatar_name', function (ws, req) {
# #     var repl_key = req.params.kata_id + "/" + req.params.avatar_name;
# #     var repl = repls[repl_key];
# #     console.log('Connected to terminal ' + repl.pid);
# #     ws.send(logs[repl.pid]);

# #     repl.on('data', function(data) {
# #         try {
# #             ws.send(data);
# #         } catch (ex) {
# #             // The WebSocket is not open, ignore
# #         }
# #     });
# #     ws.on('message', function(msg) {
# #         repl.write(msg);
# #     });
# #     ws.on('close', function () {
# #         repl.kill();
# #         console.log('Closed terminal ' + repl.pid);
# #         // Clean things up
# #         delete repls[repl_key];
# #         delete logs[repl_key];
# #     });
# # });


# if __name__ == '__main__':
#     host = '127.0.0.1' if os.name == 'nt' else '0.0.0.0'
#     port = os.environ.get('PORT', 3000)

#     print('App listening to http://{}:{}'.format(host, port))
#     socketio.run(app, host=host, port=port)
