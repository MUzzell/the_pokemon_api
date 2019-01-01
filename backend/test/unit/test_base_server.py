
import pika
import pytest
from mock import patch, MagicMock
from backend.base_server import BaseServer


@pytest.fixture
def mock_request_received(base_server):
    patched = MagicMock()
    patched.return_value = (200, 'OK')
    base_server._request_received = patched
    yield patched


@pytest.fixture
def mock_basic_properties():
    with patch(
        'pika.BasicProperties', spec=pika.BasicProperties
    ) as patched:
        patched.return_value = 123
        yield patched


@pytest.fixture
def base_server(fake_queue_name):
    yield BaseServer(fake_queue_name)


def test_setup(base_server, fake_queue_name):
    channel = MagicMock()
    base_server.setup(channel)
    channel.queue_declare.assert_called_with(queue=fake_queue_name)
    channel.basic_qos.assert_called_with(prefetch_count=1)
    channel.basic_consume.assert_called_with(
        base_server.handle_request,
        queue=fake_queue_name
    )


@pytest.mark.parametrize(
    'body, succeed', [
        (b'AA:b', True)
    ]
)
def test_handle_request(
    base_server, mock_request_received, mock_basic_properties,
    body, succeed
):

    ch = MagicMock()
    method = MagicMock()
    props = MagicMock()

    base_server.handle_request(ch, method, props, body)

    if not succeed:
        expected_body = '{"code": 403, "data": "Bad input"}'
    else:
        expected_body = '{"code": 200, "data": "OK"}'

    mock_basic_properties.assert_called_with(
        correlation_id=props.correlation_id,
        content_encoding='application/json'
    )
    ch.basic_publish.assert_called_with(
        exchange='', routing_key=props.reply_to,
        properties=mock_basic_properties.return_value,
        body=expected_body
    )
    ch.basic_ack.assert_called_with(
        delivery_tag=method.delivery_tag
    )
