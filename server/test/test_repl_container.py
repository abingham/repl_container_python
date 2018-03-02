import pytest


async def test_is_alive_responds_with_200(test_cli):
    resp = await test_cli.get('/is_alive')
    assert resp.status == 200


class TestReplCreation:
    async def test_repl_creation_responds_with_201(self, test_cli):
        resp = await test_cli.post('/', data=b'[]')
        assert resp.status == 201

    async def test_repeated_repl_creations_responds_with_409(self, test_cli):
        await test_cli.post('/', data=b'[]')
        resp = await test_cli.post('/', data=b'[]')
        assert resp.status == 409


class TestReplDeletion:
    async def test_repl_deletion_without_active_repl_responds_with_404(self, test_cli):
        resp = await test_cli.delete('/')
        assert resp.status == 404

    async def test_repl_deletion_with_active_repl_responds_with_200(self, test_cli):
        await test_cli.post('/', data=b'[]')
        resp = await test_cli.delete('/')
        assert resp.status == 200

    async def test_multiple_deletion_respond_with_404(self, test_cli):
        await test_cli.post('/', data=b'[]')
        await test_cli.delete('/')
        resp = await test_cli.delete('/')
        assert resp.status == 404


class TestReplCommunication:
    @pytest.mark.xfail(reason="sanic-pytest issue #13")
    async def test_repl_responds_with_prompt(self, test_cli):
        await test_cli.post('/', data=b'[]')
        ws_conn = await test_cli.ws_connect('/')
        try:
            msg = await ws_conn.receive()
            assert msg.data.endswith('>>>')
        finally:
            await ws_conn.close()
