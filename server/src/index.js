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

var terminalContainer = document.getElementById('terminal-container')
    // actionElements = {
    //     findNext: document.querySelector('#find-next'),
    //     findPrevious: document.querySelector('#find-previous')
    // },
    // optionElements = {
    //     cursorBlink: document.querySelector('#option-cursor-blink'),
    //     cursorStyle: document.querySelector('#option-cursor-style'),
    //     scrollback: document.querySelector('#option-scrollback'),
    //     tabstopwidth: document.querySelector('#option-tabstopwidth'),
    //     bellStyle: document.querySelector('#option-bell-style')
    // }
// ,
    // colsElement = document.getElementById('cols'),
    // rowsElement = document.getElementById('rows')
;

function setTerminalSize() {
    var cols = 70; // parseInt(colsElement.value, 10);
    var rows = 24; // parseInt(rowsElement.value, 10);
    var viewportElement = document.querySelector('.xterm-viewport');
    var scrollBarWidth = viewportElement.offsetWidth - viewportElement.clientWidth;
    var width = (cols * term.renderer.dimensions.actualCellWidth + 20 /*room for scrollbar*/).toString() + 'px';
    var height = (rows * term.renderer.dimensions.actualCellHeight).toString() + 'px';

    terminalContainer.style.width = width;
    terminalContainer.style.height = height;
    term.resize(cols, rows);
}

// colsElement.addEventListener('change', setTerminalSize);
// rowsElement.addEventListener('change', setTerminalSize);

// actionElements.findNext.addEventListener('keypress', function (e) {
//   if (e.key === "Enter") {
//     e.preventDefault();
//     term.findNext(actionElements.findNext.value);
//   }
// });
// actionElements.findPrevious.addEventListener('keypress', function (e) {
//   if (e.key === "Enter") {
//     e.preventDefault();
//     term.findPrevious(actionElements.findPrevious.value);
//   }
// });

// optionElements.cursorBlink.addEventListener('change', function () {
//   term.setOption('cursorBlink', optionElements.cursorBlink.checked);
// });
// optionElements.cursorStyle.addEventListener('change', function () {
//   term.setOption('cursorStyle', optionElements.cursorStyle.value);
// });
// optionElements.bellStyle.addEventListener('change', function () {
//   term.setOption('bellStyle', optionElements.bellStyle.value);
// });
// optionElements.scrollback.addEventListener('change', function () {
//   term.setOption('scrollback', parseInt(optionElements.scrollback.value, 10));
// });
// optionElements.tabstopwidth.addEventListener('change', function () {
//   term.setOption('tabStopWidth', parseInt(optionElements.tabstopwidth.value, 10));
// });

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

    // term.on('resize', function (size) {
    //     if (!pid) {
    //         return;
    //     }
    //     var cols = size.cols,
    //         rows = size.rows,
    //         url = '/repls/' + pid + '/size?cols=' + cols + '&rows=' + rows + '&avatar_name=' + avatar_name;

    //     fetch(url, {method: 'POST'});
    // });

    protocol = (location.protocol === 'https:') ? 'wss://' : 'ws://';
    socketURL = protocol + '//' + location.hostname + ((location.port) ? (':' + location.port) : '') + '/repls/';

    // fit is called within a setTimeout, cols and rows need this.
    setTimeout(function () {

        // Set terminal size again to set the specific dimensions on the demo
        // setTerminalSize();

        // Request creation of new repl
        fetch('/repls', {method: 'POST'}).then(function (res) {

            res.text().then(function (processId) {
                pid = processId;
                socketURL += processId;
                socket = new WebSocket(socketURL);
                socket.onopen = runRealTerminal;
                // socket.onclose = runFakeTerminal;
                // socket.onerror = runFakeTerminal;
            });
        });
    }, 0);
    // // fit is called within a setTimeout, cols and rows need this.
    // setTimeout(function () {

    //     // Set terminal size again to set the specific dimensions on the demo
    //     // setTerminalSize();
    //             // socket.on('connect', runRealTerminal);
    //     // socket.on('disconnect', runFakeTerminal);
    //     // socket.on('event', runFakeTerminal);
    // }, 0);
}

function runRealTerminal() {
    console.log('connecting terminal');
    socket.onmessage = function (event) {
        console.log(event.data);
    }
    term.attach(socket);
    term._initialized = true;
}

function runFakeTerminal() {
    // if (term._initialized) {
    //     return;
    // }

    // term._initialized = true;

    // var shellprompt = '$ ';

    // term.prompt = function () {
    //     term.write('\r\n' + shellprompt);
    // };

    // term.writeln('Welcome to xterm.js');
    // term.writeln('This is a local terminal emulation, without a real terminal in the back-end.');
    // term.writeln('Type some keys and commands to play around.');
    // term.writeln('');
    // term.prompt();

    // term.on('key', function (key, ev) {
    //     var printable = (
    //         !ev.altKey && !ev.altGraphKey && !ev.ctrlKey && !ev.metaKey
    //     );

    //     if (ev.keyCode == 13) {
    //         term.prompt();
    //     } else if (ev.keyCode == 8) {
    //         // Do not delete the prompt
    //         if (term.x > 2) {
    //             term.write('\b \b');
    //         }
    //     } else if (printable) {
    //         term.write(key);
    //     }
    // });

    // term.on('paste', function (data, ev) {
    //     term.write(data);
    // });
}
