# Python REPL in Cyber-Dojo

Our goal is to allow cyber-dojo users to start a Python REPL in the browser from
which they can import and exercise their code. At a high-level this involves two
main parts. First, there's the user interface part, the terminal where users
enter keystrokes. Second, there's backend machinery that actually runs a Python
REPL, makes user's code available to the REPL, and so forth.

## User interface

We looked at UI options first because we expected that this would drive how the
rest of the implementation would work. The technology we settled on was
[xterm.js](https://github.com/xtermjs/xterm.js). This is widely used in many
high-profile projects, so that gives us confidence that it works well. We also
found that we could get a proof-of-concept working relatively quickly.

The main aspect of xterm.js that we need to account for is that it talks via
websockets to a backend that actually runs the terminal. As a result, we need to
"punch a hole" for these websockets through cyber-dojo to the parts that run the
Python REPL (see the next section).

## repl-runner and repl-container

To manage the actual REPL processes and websocket connections to them, we'll
need two new types of container. The first container, the `repl_container`, will
be very simple. On startup it will create a Python REPL process, connect it to a
PTY, and create a websocket. It will monitor the websocket, writing the incoming
messages to the REPL. Likewise, it'll monitor the PTY and write its output (i.e.
the REPL output) to the websocket. There will be one `repl_container` for each
active REPL, i.e. one per kata/animal pair that needs an active REPL.

The second container will be the `repl_runner`. This will be started in concert
with the other long-lived containers like `web`, `nginx`, etc. This container
will run a webserver that responds to requests to start and stop REPLs. Each of
these requests will be associated with a kata/animal pair. On a `start` request,
the `repl_runner` will first start a new `repl_container` container (if one is
not already running). It will create a new server websocket connected to the
user, and it'll create a client websocket for communicating with the websocket
on the new `repl_container`. It will pipe data between these two websockets,
thereby acting as the "router" between all external websockets and those on the
`repl_containers`.

## Putting it together

We envision an overall flow something like this:

1. The `repl_runner` is started along with the `web` container. This can be
   orchestrated by the docker machinery.
2. The user requests a REPL. This will result in an HTTP request for a new REPL.
   `nginx` will be configured to proxy this call to the `repl_runner`.
3. The `repl_runner` will start a new `repl_container` as described above.
4. The UI will then talk to the websocket created by `repl_runner`, thereby
   talking to the correct `repl_container`. The kata/animal pair will be part of
   the exposed websocket URL, so the UI will have an easy time knowing how to
   communicate with the REPL.
5. When the user is done with the REPL (i.e. the exit it, press a "shutdown"
   button, or something), there will be a call to `repl_runner` to shut down the
   REPL. This will close down all of the websockets, containers (and thus REPL
   processes), etc. associated with that REPL session.

This doesn't explain how the user's code gets into the `repl_container`; I need
to investigate this a bit, but clearly it can be done.
