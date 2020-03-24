import pytest
from sanic.websocket import WebSocketProtocol

import repl_container_python.app

@pytest.yield_fixture
def app():
    yield repl_container_python.app.create_app()


@pytest.fixture(scope='function')
def test_cli(loop, app, sanic_client):
    client = sanic_client(app, protocol=WebSocketProtocol)
    return loop.run_until_complete(client)
