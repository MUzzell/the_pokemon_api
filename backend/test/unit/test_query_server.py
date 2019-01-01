import pytest
from mock import patch
from backend.query_server import QueryServer


@pytest.fixture
def query_server(fake_queue_name, mock_pokedex):
    yield QueryServer(fake_queue_name, mock_pokedex)


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
        'LEGEND': mock_pokedex.get_pokemon_by_legendary,
        'STATS': mock_pokedex.get_pokemon_by_stats
    }


@pytest.mark.parametrize(
    "q_type, arg, accepted, expected", [
        ('ID', '1', True, {"a": "123"}),
        ('ID', '1', True, None),
        ('NAME', 'a', True, []),
        ('NAME', 'a', True, [{"a": "123"}]),
        ('GEN', '1', True, []),
        ('GEN', '1', True, [{"a": 123}]),
        ('LEGEND', '0', True, []),
        ('LEGEND', '1', True, []),
        ('LEGEND', 'f', True, []),
        ('LEGEND', 't', True, []),
        ('LEGEND', 'true', True, []),
        ('LEGEND', 'false', True, []),
        ('LEGEND', 'True', True, []),
        ('LEGEND', 'False', True, []),
        ('LEGEND', '0', True, [{"a": 123}]),
        ('LEGEND', '1', True, [{"a": 123}]),
        ('LEGEND', 'f', True, [{"a": 123}]),
        ('LEGEND', 't', True, [{"a": 123}]),
        ('LEGEND', 'true', True, [{"a": 123}]),
        ('LEGEND', 'false', True, [{"a": 123}]),
        ('LEGEND', 'True', True, [{"a": 123}]),
        ('LEGEND', 'False', True, [{"a": 123}])
    ]
)
def test_handle_request(
    query_server,
    mock_pokedex, mock_query_server_publish, mock_pokedex_functions,
    q_type, arg, accepted, expected
):
    for _, f in mock_pokedex_functions.items():
        f.return_value = expected

    code, actual = query_server._request_received(q_type, arg)

    if not accepted:
        assert not any(
            [f.called for q, f in mock_pokedex_functions.items()]
        )
        assert code == 403
        assert actual == "Bad input"
        return

    mock_pokedex_functions[q_type].assert_called_with(arg)
    assert not any(
        [f.called for q, f in mock_pokedex_functions.items() if q != q_type]
    )

    if expected:
        assert code == 200
        assert actual == expected
    else:
        assert code == 404
        assert actual == "Not found"


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

    code, actual = query_server._request_received('TYPE', arg)

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
        assert code == 200
        assert actual == expected
    else:
        assert code == 404
        assert actual == "Not found"


@pytest.mark.parametrize(
    "arg, expected_call, expected", [
        ("s1 > 10", None, None),
        ("s1 >10", None, None),
        ("s1> 10", None, None),
        ("s1", None, None),
        (">", None, None),
        ("10", None, None),
        ("s1>10s", [('s1', '>', 10)], [{'id': 1}]),
        ("s1>10", [('s1', '>', 10)], [{'id': 1}]),
        ("s1>10", [('s1', '>', 10)], None),
        ("s1>10,s2>20", [('s1', '>', 10), ('s2', '>', 20)], [{'id': 1}]),
        ("s1>10 s2>20", [('s1', '>', 10), ('s2', '>', 20)], [{'id': 1}]),
    ]
)
def test_handle_request_stats(
    query_server,
    mock_pokedex, mock_query_server_publish, mock_pokedex_functions,
    arg, expected_call, expected
):
    mock_pokedex.get_pokemon_by_stats.return_value = expected

    code, actual = query_server._request_received('STATS', arg)

    if not expected_call:
        assert not mock_pokedex.get_pokemon_by_stats.called
    else:
        mock_pokedex.get_pokemon_by_stats.assert_called_with(
            expected_call
        )

    assert not any(
        [f.called for q, f in mock_pokedex_functions.items() if q != 'STATS']
    )

    if expected:
        assert code == 200
        assert actual == expected
    else:
        assert code == 404
        assert actual == "Not found"
