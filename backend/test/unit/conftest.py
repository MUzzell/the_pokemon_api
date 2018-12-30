import pytest
import mock


@pytest.fixture
def mock_redis():
    patched_redis = mock.MagicMock()
    with mock.patch(
        "redis.Redis.from_url",
        return_value=patched_redis
    ):
        yield patched_redis
