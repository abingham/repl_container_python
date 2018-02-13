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

## repl_runner

For actually running the Python REPL, the correct model seems to be a new kind
of runner. Rather than running tests (and immediately exiting), this runner will
spawn Python processes and interact with them on the user's behalf. This runner
will keep the processes alive for as long as the user is using them (we need to
think a bit about how they exit or abandon the REPL).

For each running Python process, this runner will need to expose a websocket
that the user-visible terminal reads and writes to. This is how xterm.js works,
and it seems like a reasonable approach. As mentioned above, one issue we need
to sort out is how to ensure that websocket traffic can get from the user's
browser, through the nginx and web containers, and to the repl_runner container.

An important thing to keep in mind is this runner can't just keep one long-lived
Python process for each user. Rather, it will need to launch new ones whenever a
request for a REPL is made. This way users get a clean REPL
environment/namespace/etc.

## Putting it together

We envision an overall flow something like this:

1. The `repl_runner` is started along with the `web` container. This can be
   orchestrated by the docker machinery, I think.
2. The user requests a REPL
3. In response, cyber-dojo asks the `repl_runner` to start a new REPL process,
   injecting the user's code into the container such that it can be imported
   into the REPL session. (One issue: if all Python processes are in the same
   container, how can we stop them from potentially stomping on each other's
   files? Is there a sandbox?)
4. The `repl_runner` will expose a websocket through a port for each Python
   process, and `web` will proxy websocket traffic to the correct `repl_runner`
   instance. `nginx` will need to proxy all websocket traffic to `web`.
5. When the user is done with the REPL (i.e. the exit it, press a "shutdown"
   button, or something), `repl_runner` will terminate the associated Python
   process.

So this approach will involve changes to the `nginx` container (or at least its
configuration). It will also mean similar changes to the `web` container.

 We'll also need to think about the UI changes which include:
- Adding a way to request a REPL
- Show the REPL when it's active
- Providing some means to end a REPL session
