// Simple web server for putting a Python REPL in a client's browser.

var express = require('express');
var app = express();
var expressWs = require('express-ws')(app);
var os = require('os');
var pty = require('node-pty');

var repls = {}, // TODO: Use Map instead?
    logs = {};

app.use('/build', express.static(__dirname + '/../build'));

// TODO: Presumably this UI-oriented stuff will be handled elsewhere.
app.get('/', function(req, res){
    res.sendFile(__dirname + '/index.html');
});

// Create a new REPL for the kata/avatar tuple, destroying an existing one if necessary.
app.post('/repls', function (req, res) {
    var kata_id = req.query.kata_id,
        avatar_name = req.query.avatar_name,
        cols = parseInt(req.query.cols),
        rows = parseInt(req.query.rows),
        repl = pty.spawn(
            'python', [], {
                name: 'xterm-color',  // Sets the TERM environment variable, so
                // must be 'xterm' or 'xterm-color'
                cols: cols || 80,
                rows: rows || 24,
                cwd: process.env.PWD,
                env: process.env
            }),
        repl_key = kata_id + "/" + avatar_name;

    if (repls.hasOwnProperty(repl_key)) {
        var old_repl = repls[repl_key];
        old_repl.kill();
        console.log('Closed REPL ' + old_repl.pid);
        delete repls[repl_key];
        delete logs[repl_key];
    }

    console.log('Created Python REPL with PID: ' + repl.pid);
    repls[repl_key] = repl;
    logs[repl_key] = '';
    repl.on('data', function(data) {
        logs[repl_key] += data;
    });
    res.send(repl.pid.toString());
    res.end();
});

// // Resize a repl
// app.post('/repls/:pid/size', function (req, res) {
//     var pid = parseInt(req.params.pid),
//         cols = parseInt(req.query.cols),
//         rows = parseInt(req.query.rows),
//         repl = repls[pid];

//     repl.resize(cols, rows);
//     console.log('Resized terminal ' + pid + ' to ' + cols + ' cols and ' + rows + ' rows.');
//     res.end();
// });

// Websocket for interacting with REPL
app.ws('/repls/:kata_id/:avatar_name', function (ws, req) {
    var repl_key = req.params.kata_id + "/" + req.params.avatar_name;
    var repl = repls[repl_key];
    console.log('Connected to terminal ' + repl.pid);
    ws.send(logs[repl.pid]);

    repl.on('data', function(data) {
        try {
            ws.send(data);
        } catch (ex) {
            // The WebSocket is not open, ignore
        }
    });
    ws.on('message', function(msg) {
        repl.write(msg);
    });
    ws.on('close', function () {
        repl.kill();
        console.log('Closed terminal ' + repl.pid);
        // Clean things up
        delete repls[repl_key];
        delete logs[repl_key];
    });
});

var port = process.env.PORT || 3000,
    host = os.platform() === 'win32' ? '127.0.0.1' : '0.0.0.0';

console.log('App listening to http://' + host + ':' + port);
app.listen(port, host);
