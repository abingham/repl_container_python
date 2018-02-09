import asyncio
import functools
import json
import os

from aiohttp import web
import socketio


repls = {}
logs = {}

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
    def __init__(self, sid):
        super().__init__()
        self.sid = sid

    def pipe_data_received(self, fd, data):
        print('data received from python:', data)
        loop.create_task(
            sio.emit('data',
                     data.decode('utf-8'),
                     room=self.sid,
                     namespace='/repls'))

    def process_exited(self):
        print('process exited')


async def create_repl(sid):
    print('creating repl')
    proc = await loop.subprocess_exec(
        lambda: ReplProtocol(sid),
        'python', '-i', '-u',
        )

    # proc is a tuple of (transport, protocol)
    repls[sid] = proc


# async def monitor(sid):
#     print('monitoring', sid)
#     repl = repls[sid]
#     while True:
#         if repl.returncode is not None:
#             break

#         data = await repl.stdout.read()
#         if data:
#             print('read from python:', data)
#             await sio.emit('data', data.decode('utf-8'), room=sid, namespace='/repls')
#     print('done monitoring', sid)

@sio.on('connect', namespace='/repls')
async def connect(sid, environ):
    request = environ['aiohttp.request']

    try:
        avatar_name = request.query['avatar_name']
    except KeyError:
        # TODO: return appropriate HTTP error
        raise

    print('connected with name', avatar_name)

    await create_repl(sid)
    # loop.create_task(monitor(sid))
    print('done connecting')


@sio.on('data', namespace='/repls')
async def message(sid, msg):
    print("message ", msg)
    transport, protocol = repls[sid]
    transport.get_pipe_transport(0).write(msg['data'].encode('utf-8'))

    # proc = repls[sid]
    # proc.stdin.write(msg['data'].encode('utf-8'))
    # drain = proc.stdin.drain()
    # if drain is not ():
    #     await drain

@sio.on('disconnect', namespace='/repls')
def disconnect(sid):
    print('disconnect ', sid)
    # if sid in repls:
    #     transport, protocol = repls[sid]
    #     try:
    #         transport.kill()
    #         print('Closed REPL on disconnect:', transport.get_pid())
    #     except ProcessLookupError:
    #         pass
    #     del repls[sid]

app.router.add_static('/static', 'src/static')
app.router.add_get('/', index)

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
