from sanic import Sanic

from .handlers import Handlers


def run(host, port, log_config):
    app = Sanic(log_config=log_config)

    @app.listener('after_server_stop')
    async def cleanup(app):
        handlers.kill()

    handlers = Handlers()
    app.add_route(handlers.create_repl_handler, '/', methods=['POST'])
    app.add_route(handlers.delete_repl_handler, '/',  methods=['DELETE'])
    app.add_websocket_route(handlers.websocket_handler, '/')

    app.run(host=host, port=port)
