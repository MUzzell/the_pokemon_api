import pytest
import json
from mock import call
from backend.pokedex import Pokedex

POKEMON_ID_KEY = "pokemon:id:"
POKEMON_NAME_KEY = "pokemon:name:"
POKEMON_TYPE_KEY = "pokemon:type:"
POKEMON_STATS_KEY = "pokemon:stats:"
POKEMON_LEGEND_KEY = "pokemon:legendary:"
POKEMON_GEN_KEY = "pokemon:gen:"


def has_call(mocked_func, call):
    return call in mocked_func.mock_calls


def _build_key(base, ident):
    return "{}{}".format(base, ident)


@pytest.fixture
def pokedex(mock_redis):
    yield Pokedex("")


@pytest.mark.parametrize(
    "line,will_parse,error", [
        ("1,Bulbasaur,Grass,Poison,318,45,49,49,65,65,45,1,False", True, None),
        ("4,Charmander,Fire,,309,39,52,43,60,50,65,1,False", True, None),
        ("", False, "Not enough attributes"),
        ("1,Bulbasaur,Grass,Poison,318,45,49,49,65,65,45,1", False, "Not enough attributes"),
        (",Charmander,Fire,,309,39,52,43,60,50,65,1,False", False, "No Id"),
        ("1,,Fire,,309,39,52,43,60,50,65,1,False", False, "No name"),
        ("1,Charmander,,,309,39,52,43,60,50,65,1,False", False, "Invalid Type 1"),
        ("1,Charmander,,Fire,309,39,52,43,60,50,65,1,False", False, "Invalid Type 1"),
        ("1,name,type,type,,2,3,4,5,6,7,8,False", False, "Invalid total"),
        ("1,name,type,type,a,2,3,4,5,6,7,8,False", False, "Invalid total"),
        ("1,name,type,type,1,,3,4,5,6,7,8,False", False, "Invalid HP"),
        ("1,name,type,type,1,a,3,4,5,6,7,8,False", False, "Invalid HP"),
        ("1,name,type,type,1,2,,4,5,6,7,8,False", False, "Invalid attack"),
        ("1,name,type,type,1,2,a,4,5,6,7,8,False", False, "Invalid attack"),
        ("1,name,type,type,1,2,3,,5,6,7,8,False", False, "Invalid defense"),
        ("1,name,type,type,1,2,3,a,5,6,7,8,False", False, "Invalid defense"),
        ("1,name,type,type,1,2,3,4,,6,7,8,False", False, "Invalid sp.atk"),
        ("1,name,type,type,1,2,3,4,a,6,7,8,False", False, "Invalid sp.atk"),
        ("1,name,type,type,1,2,3,4,5,,7,8,False", False, "Invalid sp.def"),
        ("1,name,type,type,1,2,3,4,5,a,7,8,False", False, "Invalid sp.def"),
        ("1,name,type,type,1,2,3,4,5,6,,8,False", False, "Invalid speed"),
        ("1,name,type,type,1,2,3,4,5,6,a,8,False", False, "Invalid speed"),
        ("1,name,type,type,1,2,3,4,5,6,7,,False", False, "Invalid generation Id"),
        ("1,name,type,type,1,2,3,4,5,6,7,a,False", False, "Invalid generation Id"),
        ("1,name,type,type,1,2,3,4,5,6,7,8,", False, "Invalid legendary"),
        ("1,name,type,type,1,2,3,4,5,6,7,8,a", False, "Invalid legendary"),
        ("1,name,type,type,1,2,3,4,5,6,7,8,falsee", False, "Invalid legendary"),
        ("1,name,type,type,1,2,3,4,5,6,7,8,truee", False, "Invalid legendary"),
        ("1,name,type,type,1,2,3,4,5,6,7,8,fa", False, "Invalid legendary"),
        ("1,name,type,type,1,2,3,4,5,6,7,8,tr", False, "Invalid legendary")
    ]
)
def test_parse_file_line(pokedex, line, will_parse, error):
    if will_parse:
        pokedex._parse_pokemon_line(line)
    else:
        try:
            pokedex._parse_pokemon_line(line)
        except ValueError as ve:
            assert ve.__str__() == error
        else:
            assert False, "ValueError not raised"


@pytest.mark.parametrize(
    "check, is_legendary", [
        ("0", False),
        ("1", True),
        ("f", False),
        ("t", True),
        ("false", False),
        ("true", True),
        ("FaLsE", False),
        ("TrUe", True),
        ("FALSE", False),
        ("TRUE", True),
        ("False", False),
        ("True", True)
    ]
)
def test_parse_legendary(pokedex, check, is_legendary):
    line = "1,name,type,type,1,2,3,4,5,6,7,8,{}".format(check)

    pokemon = pokedex._parse_pokemon_line(line)
    assert pokemon['legendary'] == is_legendary


@pytest.mark.parametrize(
    "pokemon", [
        {'id': 1, 'name': 'Bulbasaur', 'type': ['grass', 'poison'],
         'stats': {'total': 1, 'hp': 2, 'attack': 3, 'defense': 4,
                   'sp.atk': 5, 'sp.def': 6, 'speed': 7},
         'gen': 1, 'legendary': False},
        {'id': 1, 'name': 'Bulbasaur', 'type': ['grass'],
         'stats': {'total': 1, 'hp': 2, 'attack': 3, 'defense': 4,
                   'sp.atk': 5, 'sp.def': 6, 'speed': 7},
         'gen': 1, 'legendary': False},
    ]
)
@pytest.mark.parametrize(
    "exists", [True, False]
)
def test_import_pokemon(pokedex, mock_redis, pokemon, exists):
    mock_redis.get.return_value = exists
    pokedex._import_pokemon(pokemon)
    mock_redis.get.assert_called_with(
        _build_key(POKEMON_ID_KEY, pokemon['id'])
    )
    if exists:
        assert not mock_redis.set.called
        assert not mock_redis.lpush.called
    else:
        assert has_call(
            mock_redis.set,
            call(
                _build_key(POKEMON_ID_KEY, pokemon['id']),
                json.dumps(pokemon)
            )
        )
        assert has_call(
            mock_redis.set,
            call(
                _build_key(POKEMON_NAME_KEY, pokemon['name']),
                pokemon['id']
            )
        )
        assert has_call(
            mock_redis.lpush,
            call(
                _build_key(POKEMON_GEN_KEY, pokemon['gen']),
                pokemon['id']
            )
        )
        assert has_call(
            mock_redis.lpush,
            call(
                _build_key(POKEMON_LEGEND_KEY, pokemon['legendary']),
                pokemon['id']
            )
        )
        for p_type in pokemon['type']:
            assert has_call(
                mock_redis.lpush,
                call(
                    _build_key(POKEMON_TYPE_KEY, p_type.lower().strip()),
                    pokemon['id']
                )
            )
        for stat, value in pokemon['stats'].items():
            assert has_call(
                mock_redis.lpush,
                call(
                    _build_key(POKEMON_STATS_KEY, stat.lower().strip()),
                    "{}:{}".format(value, pokemon['id'])
                )
            )


def test_get_pokemon_by_id(pokedex, mock_redis):
    pokedex.get_pokemon_by_id("1")
    assert has_call(
        mock_redis.get, call(_build_key(POKEMON_ID_KEY, "1"))
    )


@pytest.mark.parametrize(
    "name, ids", [
        ('', []),
        ('name', []),
        ('name', ['a']),
        ('name', ['a', 'b'])
    ]
)
def test_get_pokemon_by_name(pokedex, mock_redis, name, ids):
    mock_redis.get.return_value = None
    mock_redis.scan.return_value = ids

    result = pokedex.get_pokemon_by_name(name)
    assert has_call(
        mock_redis.scan,
        call(match=_build_key(POKEMON_NAME_KEY, name))
    )
    if not ids:
        assert not mock_redis.get.called
        assert result == []
    else:
        assert result == [None for _ in range(len(ids))]
        for id in ids:
            assert has_call(
                mock_redis.get,
                call(_build_key(POKEMON_ID_KEY, id))
            )
