from sanic import Sanic
import sanic.response

from .handlers import Handlers


def is_alive(request):
    """Just a simple endpoint that a client can use to determine if this server is
    running.
    """
    return sanic.response.HTTPResponse(status=200)


def run(host, port, log_config):
    app = Sanic(log_config=log_config)

    @app.listener('after_server_stop')
    async def cleanup(app):
        handlers.kill()

    handlers = Handlers()
    app.add_route(handlers.create_repl_handler, '/', methods=['POST'])
    app.add_route(handlers.delete_repl_handler, '/',  methods=['DELETE'])
    app.add_websocket_route(handlers.websocket_handler, '/')

    app.add_route(is_alive, "/is_alive")

    app.run(host=host, port=port)
