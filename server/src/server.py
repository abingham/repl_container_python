import os
import selectors
import subprocess

from flask import Flask, request, url_for
app = Flask(__name__)

repls = {}
sockets = {}
logs = {}
sel = selectors.DefaultSelector()


@app.route("/")
def index():
    return app.send_static_file('index.html')


def repl_read(avatar_name, fd):
    data = os.read(fd, 1024)
    try:
        socket = sockets[avatar_name]
        socket.write(data)
    except KeyError:
        pass

    return data


# Create a new REPL for the avatar, destroying an existing one if necessary.
@app.route('/repls', methods=['POST'])
def repls():
    try:
        avatar_name = request.args['avatar_name']
        cols = int(request.args['cols'])
        rows = int(request.args['rows'])
    except KeyError:
        # TODO: return appropriate HTTP error
        raise
    except ValueError:
        # TODO: Raise appropriate HTTP error...int conversion has failed
        raise

    if avatar_name in repls:
        old_repl = repls[avatar_name]
        old_repl.kill()
        print('Closed REPL:', old_repl.pid)
        del repls[avatar_name]
        del logs[avatar_name]

    repl = subprocess.Popen('python', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    repls[avatar_name] = repl
#         repl = pty.spawn(
#             'python', [], {
#                 name: 'xterm-color',  // Sets the TERM environment variable, so
#                 // must be 'xterm' or 'xterm-color'
#                 cols: cols || 80,
#                 rows: rows || 24,
#                 cwd: process.env.PWD,
#                 env: process.env
#             }),

    print('Created Python REPL with PID:', repl.pid)
    repls[avatar_name] = repl
    logs[avatar_name] = ''

    sel.register(repl.stdout, selectors.EVENT_READ, lambda data: repl_read(avatar_name, data))

# // Websocket for interacting with REPL
# app.ws('/repls/:kata_id/:avatar_name', function (ws, req) {
#     var repl_key = req.params.kata_id + "/" + req.params.avatar_name;
#     var repl = repls[repl_key];
#     console.log('Connected to terminal ' + repl.pid);
#     ws.send(logs[repl.pid]);

#     repl.on('data', function(data) {
#         try {
#             ws.send(data);
#         } catch (ex) {
#             // The WebSocket is not open, ignore
#         }
#     });
#     ws.on('message', function(msg) {
#         repl.write(msg);
#     });
#     ws.on('close', function () {
#         repl.kill();
#         console.log('Closed terminal ' + repl.pid);
#         // Clean things up
#         delete repls[repl_key];
#         delete logs[repl_key];
#     });
# });


host = '127.0.0.1' if os.name == 'nt' else '0.0.0.0'
port = os.environ.get('PORT', 3000)

print('App listening to http://{}:{}'.format(host, port))
app.run(host=host, port=port)
