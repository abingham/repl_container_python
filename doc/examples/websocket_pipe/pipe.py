import asyncio

import aiohttp
from aiohttp import web

app = web.Application()
session = aiohttp.ClientSession()


class Router:
    async def websocket_handler(self, request):
        """Create a websocket to the caller, piping it bidirectionally with the
        websocket on the REPL container.
        """
        kata = request.match_info['kata']
        animal = request.match_info['animal']

        caller_socket = web.WebSocketResponse()
        await caller_socket.prepare(request)

        repl_socket = await session.ws_connect('http://0.0.0.0:4647/{}/{}'.format(kata, animal))

        async def pipe_repl_to_client():
            async for msg in repl_socket:
                print('received from repl:', msg.data)
                # TODO: Need to check msg.type? could be CLOSED or ERROR.
                caller_socket.send_str(msg.data)

        repl_to_client_task = request.app.loop.create_task(pipe_repl_to_client())

        async for msg in caller_socket:
            # TODO: Need to check msg.type? could be CLOSED or ERROR.
            print('received from client:', msg.data)
            repl_socket.send_str(msg.data)

        repl_to_client_task.cancel()
        await asyncio.gather(caller_socket.close(), repl_socket.close())
        return caller_socket

app = web.Application()
router = Router()
app.router.add_get('/{kata}/{animal}', router.websocket_handler)

web.run_app(app, port=4648)
