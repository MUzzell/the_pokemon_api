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


@pytest.fixture
def mock_pokedex_functions(mock_pokedex):
    yield {
        'ID': mock_pokedex.get_pokemon_by_id,
        'NAME': mock_pokedex.get_pokemon_by_name,
        'TYPE': mock_pokedex.get_pokemon_by_type,
        'GEN': mock_pokedex.get_pokemon_by_generation,
        'LEGEND': mock_pokedex.get_pokemon_by_legendary
    }


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
    "body, accepted, result", [
        (b'ID:1', True, {"a": "123"}),
        (b'ID:1', True, None),
        (b'NAME:a', True, []),
        (b'NAME:a', True, [{"a": "123"}]),
        (b'GEN:1', True, []),
        (b'GEN:1', True, [{"a": 123}]),
        (b'LEGEND:0', True, []),
        (b'LEGEND:1', True, []),
        (b'LEGEND:f', True, []),
        (b'LEGEND:t', True, []),
        (b'LEGEND:true', True, []),
        (b'LEGEND:false', True, []),
        (b'LEGEND:True', True, []),
        (b'LEGEND:False', True, []),
        (b'LEGEND:0', True, [{"a": 123}]),
        (b'LEGEND:1', True, [{"a": 123}]),
        (b'LEGEND:f', True, [{"a": 123}]),
        (b'LEGEND:t', True, [{"a": 123}]),
        (b'LEGEND:true', True, [{"a": 123}]),
        (b'LEGEND:false', True, [{"a": 123}]),
        (b'LEGEND:True', True, [{"a": 123}]),
        (b'LEGEND:False', True, [{"a": 123}])
    ]
)
def test_handle_request(
    query_server,
    mock_pokedex, mock_query_server_publish, mock_pokedex_functions,
    body, accepted, result
):
    for _, f in mock_pokedex_functions.items():
        f.return_value = result

    ch = MagicMock()
    props = MagicMock()
    method = MagicMock()

    query_server.handle_request(ch, method, props, body)

    if not accepted:
        assert not any(
            [f.called for q, f in mock_pokedex_functions.items()]
        )
        mock_query_server_publish.assert_called_with(
            ch, method, props,
            {'code': 403, 'data': "Bad input"}
        )
        return

    q_type, arg = body.decode('ASCII').split(':')

    mock_pokedex_functions[q_type].assert_called_with(arg)
    assert not any(
        [f.called for q, f in mock_pokedex_functions.items() if q != q_type]
    )

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
    query_server,
    mock_pokedex, mock_query_server_publish, mock_pokedex_functions,
    arg, expected_call, expected
):

    mock_pokedex.get_pokemon_by_type.return_value = expected
    ch = MagicMock()
    props = MagicMock()
    method = MagicMock()

    body = bytes('TYPE:{}'.format(arg), 'ASCII')
    query_server.handle_request(ch, method, props, body)

    if not expected_call:
        assert not mock_pokedex.get_pokemon_by_type.called
    else:
        mock_pokedex.get_pokemon_by_type.assert_called_with(
            expected_call
        )

    assert not any(
        [f.called for q, f in mock_pokedex_functions.items() if q != 'TYPE']
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
