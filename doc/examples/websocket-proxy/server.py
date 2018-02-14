import logging.config
import sys

from aiohttp import web

logging.config.dictConfig({
    'version': 1,
    'handlers': {
        'console': {
            'class' : 'logging.StreamHandler',
            # 'formatter': brief,
            'level'   : logging.INFO,
            'stream'  : 'ext://sys.stdout'
        }
    },
    'loggers': {
        'aiohttp.access': {
            'level': logging.INFO,
            'handlers': ['console']
        }
    }
})

async def websocket_handler(request):
    """Create a new websocket and connect it's input and output to the subprocess
    with the specified PID.
    """

    kata = request.match_info['kata']
    animal = request.match_info['animal']
    print('ws connection:', kata, animal)

    socket = web.WebSocketResponse()
    await socket.prepare(request)

    async for msg in socket:
        print('received ({}/{}): {}'.format(kata, animal, msg.data))
        await socket.send_str('server received from client: ' + msg.data)

    print('closing {}{}'.format(kata, animal))
    await socket.close()
    return socket


app = web.Application()
app.router.add_get('/{kata}/{animal}', websocket_handler)

web.run_app(app, port=4647)
