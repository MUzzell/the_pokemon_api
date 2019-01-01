import pytest
import mock


def has_call(mocked_func, call):
    return call in mocked_func.mock_calls


@pytest.fixture
def fake_queue_name():
    yield "qq"


@pytest.fixture
def mock_redis():
    patched_redis = mock.MagicMock()
    with mock.patch(
        "redis.Redis.from_url",
        return_value=patched_redis
    ):
        yield patched_redis


@pytest.fixture
def mock_pokedex():
    yield mock.MagicMock()
