import logging

import sanic.exceptions
import sanic.response

from .repl_manager import ReplManager

log = logging.getLogger()


class Handlers:
    """Handlers for various routes in the app, plus attributes for tracking the
    REPL process.
    """

    def __init__(self):
        self.repl_mgr = None

    def close(self):
        if self.repl_mgr is not None:
            log.info('destroying REPL')
            self.repl_mgr.close()
            self.repl_mgr = None

        assert self.repl_mgr is None

    async def create_repl_handler(self, request):
        log.info("wama lama ding dong")
        if self.repl_mgr is not None:
            log.info('request to create REPL while one already exists')
            return sanic.response.HTTPResponse(status=409)

        log.info('creating REPL')

        self.repl_mgr = ReplManager(request.app.loop,
                                    request.json)

        # TODO: Detect and respond to failures in creating the ReplManager

        return sanic.response.HTTPResponse(status=201)  # created

    async def delete_repl_handler(self, request):
        # If there's not extant REPL, slap 'em with a 404
        if self.repl_mgr is None:
            return sanic.response.HTTPResponse(status=404)

        self.close()

        # TODO: Detect and respond to failures in closure

        return sanic.response.HTTPResponse(status=200)  # OK

    async def websocket_handler(self, request, ws):
        """Create a new websocket and connect it's input and output to the subprocess
        with the specified PID.
        """

        if self.repl_mgr is None:
            return sanic.response.HTTPResponse(status=404)

        log.info('initiating websocket')
        await self.repl_mgr.process_websocket(ws)
        log.info('terminating websocket')
