import pytest
import mock


@pytest.fixture
def fake_query_queue():
    yield "qq"


@pytest.fixture
def fake_battle_queue():
    yield "bq"


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
