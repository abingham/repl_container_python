from aiohttp import web

from .handlers import Handlers


def run(port):
    app = web.Application()
    handlers = Handlers()

    async def cleanup(app):
        handlers.kill()

    app.on_shutdown.append(cleanup)

    app.router.add_post('/', handlers.create_repl_handler)
    app.router.add_delete('/', handlers.delete_repl_handler)
    app.router.add_get('/', handlers.websocket_handler)

    web.run_app(app, port=port)
