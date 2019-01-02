import pytest
from backend.battle_server import BattleServer


@pytest.fixture
def battle_server(fake_queue_name, mock_pokedex):
    yield BattleServer(fake_queue_name, mock_pokedex)


@pytest.fixture
def dummy_pokemon_setup(mock_pokedex):
    pokemon = {
        '1': {
            'name': 'POKE_A',
            'stats': {
                'attack': 50,
                'defence': 10,
                'speed': 20,
                'hp': 400
            }
        },
        '2': {
            'name': 'POKE_B',
            'stats': {
                'attack': 40,
                'defence': 15,
                'speed': 30,
                'hp': 325
            }
        },
        '3': {
            'name': 'POKE_C',
            'stats': {
                'attack': 40,
                'defence': 15,
                'speed': 25,
                'hp': 100
            }
        },
        '4': {
            'name': 'POKE_D',
            'stats': {
                'attack': 40,
                'defence': 45,
                'speed': 30,
                'hp': 100
            }
        }
    }

    def mock_get_by_id(pid):
        if pid not in pokemon:
            return None
        return pokemon[pid]

    mock_pokedex.get_pokemon_by_id = mock_get_by_id
    yield pokemon


@pytest.mark.parametrize(
    'args', [
        ('AA'),
        ('AA' ''),
        ('AA', '1'),
        ('AA', '1', ''),
        ('AA', '', '1'),
        ('AA', '1', '1', '')
    ]
)
def test_request_received_input_checking(
    battle_server, mock_pokedex, dummy_pokemon_setup,
    args
):
    code, result = battle_server._request_received(args)

    assert code == 403
    assert result == "Bad input"


@pytest.mark.parametrize(
    'args, expected_code, err_msg', [
        (('AA', '1', '2'), 200, None),
        (('AA', '2', '3'), 200, None),
        (('AA', '1', '5'), 404, "Could not find pokemon"),
        (('AA', '5', '1'), 404, "Could not find pokemon")
    ]
)
def test_request_received_id_validation(
    battle_server, mock_pokedex, dummy_pokemon_setup,
    args, expected_code, err_msg
):
    code, result = battle_server._request_received(*args)

    assert code == expected_code

    if err_msg:
        assert result == err_msg


@pytest.mark.parametrize(
    'ident, expected', [
        (('AA', '1', '2'), {
            'combatants': ['POKE_A', 'POKE_B'],
            1: [{'attacker': 1, 'defender': 0,
                 'damage': 30, 'hp': 370},
                {'attacker': 0, 'defender': 1,
                 'damage': 35, 'hp': 290}],
            2: [{'attacker': 1, 'defender': 0,
                 'damage': 30, 'hp': 340},
                {'attacker': 0, 'defender': 1,
                 'damage': 35, 'hp': 255}],
            3: [{'attacker': 1, 'defender': 0,
                 'damage': 30, 'hp': 310},
                {'attacker': 0, 'defender': 1,
                 'damage': 35, 'hp': 220}],
            4: [{'attacker': 1, 'defender': 0,
                 'damage': 30, 'hp': 280},
                {'attacker': 0, 'defender': 1,
                 'damage': 35, 'hp': 185}],
            5: [{'attacker': 1, 'defender': 0,
                 'damage': 30, 'hp': 250},
                {'attacker': 0, 'defender': 1,
                 'damage': 35, 'hp': 150}],
            6: [{'attacker': 1, 'defender': 0,
                 'damage': 30, 'hp': 220},
                {'attacker': 0, 'defender': 1,
                 'damage': 35, 'hp': 115}],
            7: [{'attacker': 1, 'defender': 0,
                 'damage': 30, 'hp': 190},
                {'attacker': 0, 'defender': 1,
                 'damage': 35, 'hp': 80}],
            8: [{'attacker': 1, 'defender': 0,
                 'damage': 30, 'hp': 160},
                {'attacker': 0, 'defender': 1,
                 'damage': 35, 'hp': 45}],
            }),
        (('AA', '2', '1'), {
            'combatants': ['POKE_B', 'POKE_A'],
            1: [{'attacker': 0, 'defender': 1,
                 'damage': 30, 'hp': 370},
                {'attacker': 1, 'defender': 0,
                 'damage': 35, 'hp': 290}],
            2: [{'attacker': 0, 'defender': 1,
                 'damage': 30, 'hp': 340},
                {'attacker': 1, 'defender': 0,
                 'damage': 35, 'hp': 255}],
            3: [{'attacker': 0, 'defender': 1,
                 'damage': 30, 'hp': 310},
                {'attacker': 1, 'defender': 0,
                 'damage': 35, 'hp': 220}],
            4: [{'attacker': 0, 'defender': 1,
                 'damage': 30, 'hp': 280},
                {'attacker': 1, 'defender': 0,
                 'damage': 35, 'hp': 185}],
            5: [{'attacker': 0, 'defender': 1,
                 'damage': 30, 'hp': 250},
                {'attacker': 1, 'defender': 0,
                 'damage': 35, 'hp': 150}],
            6: [{'attacker': 0, 'defender': 1,
                 'damage': 30, 'hp': 220},
                {'attacker': 1, 'defender': 0,
                 'damage': 35, 'hp': 115}],
            7: [{'attacker': 0, 'defender': 1,
                 'damage': 30, 'hp': 190},
                {'attacker': 1, 'defender': 0,
                 'damage': 35, 'hp': 80}],
            8: [{'attacker': 0, 'defender': 1,
                 'damage': 30, 'hp': 160},
                {'attacker': 1, 'defender': 0,
                 'damage': 35, 'hp': 45}],
            }),
        (('AA', '2', '3'), {
            'combatants': ['POKE_B', 'POKE_C'],
            1: [{'attacker': 0, 'defender': 1,
                 'damage': 25, 'hp': 75},
                {'attacker': 1, 'defender': 0,
                 'damage': 25, 'hp': 300}],
            2: [{'attacker': 0, 'defender': 1,
                 'damage': 25, 'hp': 50},
                {'attacker': 1, 'defender': 0,
                 'damage': 25, 'hp': 275}],
            3: [{'attacker': 0, 'defender': 1,
                 'damage': 25, 'hp': 25},
                {'attacker': 1, 'defender': 0,
                 'damage': 25, 'hp': 250}],
            4: [{'attacker': 0, 'defender': 1,
                 'damage': 25, 'hp': 0}]
            }),
        (('AA', '3', '2'), {
            'combatants': ['POKE_C', 'POKE_B'],
            1: [{'attacker': 1, 'defender': 0,
                 'damage': 25, 'hp': 75},
                {'attacker': 0, 'defender': 1,
                 'damage': 25, 'hp': 300}],
            2: [{'attacker': 1, 'defender': 0,
                 'damage': 25, 'hp': 50},
                {'attacker': 0, 'defender': 1,
                 'damage': 25, 'hp': 275}],
            3: [{'attacker': 1, 'defender': 0,
                 'damage': 25, 'hp': 25},
                {'attacker': 0, 'defender': 1,
                 'damage': 25, 'hp': 250}],
            4: [{'attacker': 1, 'defender': 0,
                 'damage': 25, 'hp': 0}]
            }),
        (('AA', '1', '3'), {
            'combatants': ['POKE_A', 'POKE_C'],
            1: [{'attacker': 1, 'defender': 0,
                 'damage': 30, 'hp': 370},
                {'attacker': 0, 'defender': 1,
                 'damage': 35, 'hp': 65}],
            2: [{'attacker': 1, 'defender': 0,
                 'damage': 30, 'hp': 340},
                {'attacker': 0, 'defender': 1,
                 'damage': 35, 'hp': 30}],
            3: [{'attacker': 1, 'defender': 0,
                 'damage': 30, 'hp': 310},
                {'attacker': 0, 'defender': 1,
                 'damage': 35, 'hp': 0}],
            }),
        (('AA', '3', '1'), {
            'combatants': ['POKE_C', 'POKE_A'],
            1: [{'attacker': 0, 'defender': 1,
                 'damage': 30, 'hp': 370},
                {'attacker': 1, 'defender': 0,
                 'damage': 35, 'hp': 65}],
            2: [{'attacker': 0, 'defender': 1,
                 'damage': 30, 'hp': 340},
                {'attacker': 1, 'defender': 0,
                 'damage': 35, 'hp': 30}],
            3: [{'attacker': 0, 'defender': 1,
                 'damage': 30, 'hp': 310},
                {'attacker': 1, 'defender': 0,
                 'damage': 35, 'hp': 0}],
            }),
        (('AA', '2', '4'), {
            'combatants': ['POKE_B', 'POKE_D'],
            1: [{}]
            })
    ]
)
def test_request_received_battle_results(
    battle_server, mock_pokedex, dummy_pokemon_setup,
    ident, expected
):
    code, result = battle_server._request_received(*ident)
    assert code == 200
    assert result == expected


def test_request_received_equal_speed(
    battle_server, mock_pokedex, dummy_pokemon_setup
):

    attempts = 3

    dummy_pokemon_setup['4'] = {
        'name': 'POKE_A',
        'stats': {
            'attack': 50,
            'defence': 10,
            'speed': 20,
            'hp': 400
        }
    }

    # Since the test includes random, there is a chance that the
    # first pokemon may always hit first, or vice versa.
    # this loop therefore accomodates that, but only to a point.
    for i in range(attempts):
        code, results = battle_server._request_received(
            'A', '1', '4'
        )
        assert code == 200
        assert results['combatants'] == ['POKE_A', 'POKE_A']
        results.pop('combatants')
        attacked_first = [a[0]['attacker'] for _, a in results.items()]

        if 0 in attacked_first and 1 in attacked_first:
            return

        # A reset of the pokemon's health has to be done here
        # because the dict (which would be unique per session in
        # prod) is shared for the test
        dummy_pokemon_setup['4']['stats']['health'] = 400
        dummy_pokemon_setup['1']['stats']['health'] = 400

    assert False
