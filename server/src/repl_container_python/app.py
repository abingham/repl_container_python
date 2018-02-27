import logging

from sanic import Sanic
import sanic.response

from .handlers import Handlers
from .logging import logging_config


def is_alive(request):
    """Just a simple endpoint that a client can use to determine if this server is
    running.
    """
    return sanic.response.HTTPResponse(status=200)


def create_app(log_level=logging.WARN):
    app = Sanic(logging_config(log_level))

    @app.listener('before_server_stop')
    async def cleanup(app, loop):
        handlers.kill()

    handlers = Handlers()
    app.add_route(handlers.create_repl_handler, '/', methods=['POST'])
    app.add_route(handlers.delete_repl_handler, '/',  methods=['DELETE'])
    app.add_websocket_route(handlers.websocket_handler, '/')

    app.add_route(is_alive, "/is_alive")

    return app
