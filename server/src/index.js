require('../node_modules/xterm/dist/xterm.css');
require('../node_modules/xterm/dist/addons/fullscreen/fullscreen.css');
require('./style.css');

import { Terminal } from 'xterm';
import * as attach from 'xterm/lib/addons/attach/attach';
import * as fit from 'xterm/lib/addons/fit/fit';
import * as fullscreen from 'xterm/lib/addons/fullscreen/fullscreen';
import * as search from 'xterm/lib/addons/search/search';
import * as winptyCompat from 'xterm/lib/addons/winptyCompat/winptyCompat';
import io from 'socket.io-client';

Terminal.applyAddon(attach);
Terminal.applyAddon(fit);
Terminal.applyAddon(fullscreen);
Terminal.applyAddon(search);
Terminal.applyAddon(winptyCompat);

var term,
    protocol,
    socketURL,
    socket,
    pid;

var terminalContainer = document.getElementById('terminal-container') ;

function setTerminalSize() {
    var cols = 70;
    var rows = 24;
    var viewportElement = document.querySelector('.xterm-viewport');
    var scrollBarWidth = viewportElement.offsetWidth - viewportElement.clientWidth;
    var width = (cols * term.renderer.dimensions.actualCellWidth + 20 /*room for scrollbar*/).toString() + 'px';
    var height = (rows * term.renderer.dimensions.actualCellHeight).toString() + 'px';

    terminalContainer.style.width = width;
    terminalContainer.style.height = height;
    term.resize(cols, rows);
}

createTerminal();

function createTerminal() {
    var avatar_name = 'test_avatar';
    term = new Terminal({
        cursorBlink: true, // optionElements.cursorBlink.checked,
        scrollback: 10, // parseInt(optionElements.scrollback.value, 10),
        tabStopWidth: 10 // parseInt(optionElements.tabstopwidth.value, 10)
    });
    window.term = term;
    term.open(terminalContainer);
    term.winptyCompatInit();
    term.fit();
    term.focus();

    protocol = (location.protocol === 'https:') ? 'wss://' : 'ws://';
    socketURL = protocol + '//' + location.hostname + ((location.port) ? (':' + location.port) : '') + '/repls/';

    // Request creation of new repl
    fetch('/repls', {method: 'POST'}).then(function (res) {
        res.text().then(function (processId) {
            pid = processId;
            socketURL += processId;
            socket = new WebSocket(socketURL);
            socket.onopen = function() {
                term.attach(socket);
                term._initialize = true;
            }
        });
    });
}
