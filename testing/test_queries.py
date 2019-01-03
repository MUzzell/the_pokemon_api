import pytest
import requests
import os


@pytest.fixture(scope='session')
def host():
    return os.getenv("TEST_HOST", 'frontend')


@pytest.fixture(scope='session')
def port():
    return os.getenv("TEST_PORT", 5000)


def _send_request(host, port, action, ident):
    return requests.get(
        "http://{}:{}/{}/{}".format(
            host, port, action, ident)
    )


@pytest.mark.parametrize(
    "ident,code,expected", [
        ('doesnotexist', 404, 'Not found'),
        ('999', 404, 'Not found'),
        ('2', 200,
         {"id": "2", "name": "Ivysaur",
          "type": ["Grass", "Poison"],
          "stats": {"total": 405, "hp": 60,
                    "attack": 62, "defence": 63,
                    "sp.atk": 80, "sp.def": 80,
                    "speed": 60},
          "gen": 1, "legendary": False})
    ]
)
def test_query_by_id(
    host, port,
    ident, code, expected
):
    response = _send_request(host, port, 'id', ident)

    assert response.status_code == code
    assert response.json() == expected


@pytest.mark.parametrize(
    "ident,code,expected", [
        ('doesnotexist', 404, 'Not found'),
        ('Bulbasaur', 200,
         [{"id": "1", "name": "Bulbasaur", "type": ["Grass", "Poison"],
           "stats": {"total": 318, "hp": 45, "attack": 49, "defence": 49,
                     "sp.atk": 65, "sp.def": 65, "speed": 45},
           "gen": 1, "legendary": False}]),
        ('Bulba*', 200,
         [{"id": "1", "name": "Bulbasaur", "type": ["Grass", "Poison"],
           "stats": {"total": 318, "hp": 45, "attack": 49, "defence": 49,
                     "sp.atk": 65, "sp.def": 65, "speed": 45},
           "gen": 1, "legendary": False}]),
        ('*chu', 200,
         [{"id": "26", "name": "Raichu", "type": ["Electric"],
           "stats": {"total": 485, "hp": 60, "attack": 90, "defence": 55,
                     "sp.atk": 90, "sp.def": 80, "speed": 110},
           "gen": 1, "legendary": False},
          {"id": "172", "name": "Pichu", "type": ["Electric"],
           "stats": {"total": 205, "hp": 20, "attack": 40, "defence": 15,
                     "sp.atk": 35, "sp.def": 35, "speed": 60},
           "gen": 2, "legendary": False},
          {"id": "25", "name": "Pikachu", "type": ["Electric"],
           "stats": {"total": 320, "hp": 35, "attack": 55, "defence": 40,
                     "sp.atk": 50, "sp.def": 50, "speed": 90},
           "gen": 1, "legendary": False}])
    ]
)
def test_query_by_name(
    host, port,
    ident, code, expected
):
    response = _send_request(host, port, 'name', ident)

    assert response.status_code == code
    actual = response.json()
    if code == 200:
        assert len(actual) == len(expected)
        for expected_p in expected:
            assert expected_p in actual
    else:
        assert actual == expected
