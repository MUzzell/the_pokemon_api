import pytest
from mock import MagicMock, patch
from backend.query_server import QueryServer


@pytest.fixture
def query_server(fake_query_queue, mock_pokedex):
    yield QueryServer(fake_query_queue, mock_pokedex)


@pytest.fixture
def mock_query_server_publish():
    with patch(
        "backend.query_server.QueryServer._publish"
    ) as patched:
        yield patched


def test_setup(query_server, fake_query_queue, mock_pokedex):
    channel = MagicMock()
    query_server.setup(channel)
    channel.queue_declare.assert_called_with(queue=fake_query_queue)
    channel.basic_qos.assert_called_with(prefetch_count=1)
    channel.basic_consume.assert_called_with(
        query_server.handle_request,
        queue=fake_query_queue
    )


@pytest.mark.parametrize(
    "q_type, arg, result", [
        ("ID", "1", {"a": "123"}),
        ("NAME", "a", [{"a": "123"}]),
        ("ID", "1", None),
        ("NAME", "a", [])
    ]
)
def test_handle_request_name_id(
    query_server, mock_pokedex, mock_query_server_publish,
    q_type, arg, result
):
    mock_pokedex.get_pokemon_by_id.return_value = result
    mock_pokedex.get_pokemon_by_name.return_value = result
    ch = MagicMock()
    props = MagicMock()
    method = MagicMock()

    body = bytes('{}:{}'.format(q_type, arg), 'ASCII')

    query_server.handle_request(ch, method, props, body)

    if q_type == 'ID':
        mock_pokedex.get_pokemon_by_id.assert_called_with(arg)
        assert not mock_pokedex.get_pokemon_by_name.called
    elif q_type == 'NAME':
        mock_pokedex.get_pokemon_by_name.assert_called_with(arg)
        assert not mock_pokedex.get_pokemon_by_id.called

    if result:
        mock_query_server_publish.assert_called_with(
            ch, method, props,
            {'code': 200, 'data': result}
        )
    else:
        mock_query_server_publish.assert_called_with(
            ch, method, props,
            {'code': 404, 'data': "Not found"}
        )


@pytest.mark.parametrize(
    "arg, expected_call, expected", [
        ("", '', []),
        ("t", ['t'], []),
        ("t", ['t'], [{"a": "123"}]),
        (",", '', []),
        ("t,", ['t'], []),
        (",t", ['t'], []),
        ("t,", ['t'], [{"a": "123"}]),
        (",t", ['t'], [{"a": "123"}]),
        ("ta,tb", ['ta', 'tb'], []),
        ("ta,tb", ['ta', 'tb'], [{"a": "123"}, {"b": "456"}])
    ]
)
def test_handle_request_type(
    query_server, mock_pokedex, mock_query_server_publish,
    arg, expected_call, expected
):

    mock_pokedex.get_pokemon_by_type.return_value = expected
    ch = MagicMock()
    props = MagicMock()
    method = MagicMock()

    body = bytes('TYPE:{}'.format(arg), 'ASCII')
    query_server.handle_request(ch, method, props, body)

    assert not mock_pokedex.get_pokemon_by_id.called
    assert not mock_pokedex.get_pokemon_by_name.called

    if not expected_call:
        assert not mock_pokedex.get_pokemon_by_type.called
    else:
        mock_pokedex.get_pokemon_by_type.assert_called_with(
            expected_call
        )

    if expected:
        mock_query_server_publish.assert_called_with(
            ch, method, props,
            {'code': 200, 'data': expected}
        )
    else:
        mock_query_server_publish.assert_called_with(
            ch, method, props,
            {'code': 404, 'data': 'Not found'}
        )
