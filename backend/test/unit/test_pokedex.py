import pytest
import json
from mock import call
from backend.pokedex import Pokedex

from conftest import has_call

POKEMON_ID_KEY = "pokemon:id:"
POKEMON_NAME_KEY = "pokemon:name:"
POKEMON_TYPE_KEY = "pokemon:type:"
POKEMON_STATS_KEY = "pokemon:stats:"
POKEMON_LEGEND_KEY = "pokemon:legendary:"
POKEMON_GEN_KEY = "pokemon:gen:"


def _build_key(base, ident):
    if isinstance(ident, str):
        ident = ident.lower().strip()
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
        ("1,name,type,type,1,2,3,,5,6,7,8,False", False, "Invalid defence"),
        ("1,name,type,type,1,2,3,a,5,6,7,8,False", False, "Invalid defence"),
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
         'stats': {'total': 1, 'hp': 2, 'attack': 3, 'defence': 4,
                   'sp.atk': 5, 'sp.def': 6, 'speed': 7},
         'gen': 1, 'legendary': False},
        {'id': 1, 'name': 'Bulbasaur', 'type': ['grass'],
         'stats': {'total': 1, 'hp': 2, 'attack': 3, 'defence': 4,
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
                    pokemon['id']
                )
            )


def test_get_pokemon_by_id(pokedex, mock_redis):
    mock_redis.get.return_value = b'{"a": 123}'
    result = pokedex.get_pokemon_by_id("1")
    assert result == {"a": 123}
    assert has_call(
        mock_redis.get, call(_build_key(POKEMON_ID_KEY, "1"))
    )


@pytest.mark.parametrize(
    "name, ids", [
        ('name', []),
        ('name', ['a']),
        ('name', ['a', 'b'])
    ]
)
def test_get_pokemon_by_name(pokedex, mock_redis, name, ids):
    mock_redis.get.return_value = b'1'
    mock_redis.scan_iter.return_value = ids

    result = pokedex.get_pokemon_by_name(name)
    assert has_call(
        mock_redis.scan_iter,
        call(match=_build_key(POKEMON_NAME_KEY, name))
    )
    if not ids:
        assert not mock_redis.get.called
        assert result == []
    else:
        assert result == [1 for _ in range(len(ids))]
        assert mock_redis.get.call_count == len(ids) * 2
        for ident in ids:
            assert has_call(
                mock_redis.get,
                call(ident)
            )
            assert has_call(
                mock_redis.get,
                call(_build_key(POKEMON_ID_KEY, '1'))
            )


@pytest.mark.parametrize(
    "p_type, ids", [
        ('type', []),
        ('type', [b'a']),
        ('type', [b'a', b'b'])
    ]
)
def test_get_pokemon_of_type(pokedex, mock_redis, p_type, ids):
    mock_redis.get.return_value = b'1'
    mock_redis.lrange.return_value = ids

    result = pokedex.get_pokemon_of_type(p_type)
    assert has_call(
        mock_redis.lrange,
        call(_build_key(POKEMON_TYPE_KEY, p_type), 0, -1)
    )
    if not ids:
        assert not mock_redis.get.called
        assert result == []
    else:
        for ident in ids:
            assert has_call(
                mock_redis.get,
                call(_build_key(POKEMON_ID_KEY, 'a'))
            )


@pytest.mark.parametrize(
    "data, expected", [
        ({'type_a': []}, []),
        ({'type_a': [{'id': 1}, {'id': 2}]}, [{'id': 1}, {'id': 2}]),
        ({'type_a': [{'id': 1}]}, [{'id': 1}]),
        ({'type_a': [{'id': 1}], 'type_b': []}, []),
        ({'type_a': [], 'type_b': [{'id': 1}]}, []),
        ({'type_a': [{'id': 1}], 'type_b': [{'id': 1}]}, [{'id': 1}]),
        ({'type_a': [{'id': 1}, {'id': 2}], 'type_b': [{'id': 1}]}, [{'id': 1}]),
        ({'type_a': [{'id': 1}], 'type_b': [{'id': 1}, {'id': 2}]}, [{'id': 1}]),
        ({'type_a': [{'id': 1}, {'id': 2}], 'type_b': [{'id': 1}, {'id': 2}]}, [{'id': 1}, {'id': 2}])
    ]
)
def test_get_pokemon_by_type(
    pokedex, mock_redis,
    data, expected
):
    def mock_get_pokemon_of_type(ptype):
        return data[ptype]

    pokedex.get_pokemon_of_type = mock_get_pokemon_of_type

    actual = pokedex.get_pokemon_by_type(data.keys())

    assert actual == expected


@pytest.mark.parametrize(
    "stats, data, expected", [
        (
            [('s1', '=', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 10}}]},
            [{'id': 1, 'stats': {'s1': 10}}]
        ),
        (
            [('s1', '=', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 20}}]},
            []
        ),
        (
            [('s1', '>', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 10}}]},
            []
        ),
        (
            [('s1', '>', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 9}}]},
            []
        ),
        (
            [('s1', '>', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 11}}]},
            [{'id': 1, 'stats': {'s1': 11}}]
        ),
        (
            [('s1', '<', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 9}}]},
            [{'id': 1, 'stats': {'s1': 9}}]
        ),
        (
            [('s1', '<', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 10}}]},
            []
        ),
        (
            [('s1', '<', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 11}}]},
            []
        ),
        (
            [('s1', '<=', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 10}}]},
            [{'id': 1, 'stats': {'s1': 10}}]
        ),
        (
            [('s1', '<=', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 9}}]},
            [{'id': 1, 'stats': {'s1': 9}}]
        ),
        (
            [('s1', '<=', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 11}}]},
            []
        ),
        (
            [('s1', '=>', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 10}}]},
            [{'id': 1, 'stats': {'s1': 10}}]
        ),
        (
            [('s1', '=>', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 11}}]},
            [{'id': 1, 'stats': {'s1': 11}}]
        ),
        (
            [('s1', '=>', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 9}}]},
            []
        ),
        (
            [('s1', '=', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 10, 's2': 20}}],
             's2': [{'id': 1, 'stats': {'s1': 10, 's2': 20}}]},
            [{'id': 1, 'stats': {'s1': 10, 's2': 20}}]
        ),
        (
            [('s2', '=', 10)],
            {'s1': [{'id': 1, 'stats': {'s1': 10, 's2': 20}}],
             's2': [{'id': 1, 'stats': {'s1': 10, 's2': 20}}]},
            []
        ),
        (
            [('s2', '=', 20)],
            {'s1': [{'id': 1, 'stats': {'s1': 10, 's2': 20}}],
             's2': [{'id': 1, 'stats': {'s1': 10, 's2': 20}}]},
            [{'id': 1, 'stats': {'s1': 10, 's2': 20}}]
        ),
        (
            [('s1', '=', 10), ('s2', '=', 20)],
            {'s1': [{'id': 1, 'stats': {'s1': 10, 's2': 20}}],
             's2': [{'id': 1, 'stats': {'s1': 10, 's2': 20}}]},
            [{'id': 1, 'stats': {'s1': 10, 's2': 20}}]
        ),
        (
            [('s1', '=', 20), ('s2', '=', 20)],
            {'s1': [{'id': 1, 'stats': {'s1': 10, 's2': 20}}],
             's2': [{'id': 1, 'stats': {'s1': 10, 's2': 20}}]},
            []
        ),
        (
            [('s1', '=', 10), ('s2', '>', 20)],
            {'s1': [{'id': 1, 'stats': {'s1': 10, 's2': 20}}],
             's2': [{'id': 1, 'stats': {'s1': 10, 's2': 20}}]},
            []
        ),
        (
            [('s1', '=', 10), ('s2', '=', 20)],
            {'s1': [{'id': 1, 'stats': {'s1': 10, 's2': 20}}],
             's2': []},
            []
        ),

    ]
)
def test_get_pokemon_by_stats(
    pokedex, mock_redis,
    stats, data, expected
):
    def mock_get_pokemon_by_stat(stat):
        return data[stat]

    pokedex.get_pokemon_by_stat = mock_get_pokemon_by_stat

    actual = pokedex.get_pokemon_by_stats(stats)

    assert actual == expected


@pytest.mark.parametrize(
    "gen, expected", [
        ('1', []),
        ('1', [{'id': 1}]),
        ('1', [{'id': 1}]),
        ('1', [{'id': 1}, {'id': 1}])
    ]
)
def test_get_pokemon_by_generation(
    pokedex, mock_redis,
    gen, expected
):
    mock_redis.lrange.return_value = [b'1' for _ in range(len(expected))]
    mock_redis.get.return_value = b'{"id": 1}'

    actual = pokedex.get_pokemon_by_generation(gen)

    mock_redis.lrange.assert_called_with(
        _build_key(POKEMON_GEN_KEY, gen), 0, -1
    )
    assert actual == expected
    if expected:
        mock_redis.get.assert_called_with(
            _build_key(POKEMON_ID_KEY, 1)
        )
    else:
        assert not mock_redis.get.called


@pytest.mark.parametrize(
    "is_legend, expected", [
        (True, []),
        (False, []),
        (True, [{'id': 1}]),
        (False, [{'id': 1}]),
        (True, [{'id': 1}]),
        (False, [{'id': 1}, {'id': 1}])
    ]
)
def test_get_pokemon_by_legendary(
    pokedex, mock_redis,
    is_legend, expected
):
    mock_redis.lrange.return_value = [b'1' for _ in range(len(expected))]
    mock_redis.get.return_value = b'{"id": 1}'

    actual = pokedex.get_pokemon_by_legendary(is_legend)

    mock_redis.lrange.assert_called_with(
        _build_key(POKEMON_LEGEND_KEY, is_legend), 0, -1
    )
    assert actual == expected
    if expected:
        mock_redis.get.assert_called_with(
            _build_key(POKEMON_ID_KEY, 1)
        )
    else:
        assert not mock_redis.get.called
