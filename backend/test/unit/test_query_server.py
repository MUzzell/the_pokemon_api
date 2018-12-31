import pytest
import json
import pika
from mock import MagicMock, call, patch
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
        ("NAME", "a", {"a": "123"}),
        ("ID", "1", ''),
        ("NAME", "a", '')
    ]
)
def test_handle_request(
    query_server, mock_pokedex, mock_query_server_publish,
    q_type, arg, result
):
    mock_pokedex.get_pokemon_by_id.return_value = result
    mock_pokedex.get_pokemon_by_name.return_value = result
    ch = MagicMock()
    props = MagicMock()
    props.correlation_id = 123
    props.reply_to = 456
    method = MagicMock()
    method.delivery_tag = 789

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
