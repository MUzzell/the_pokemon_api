
import random

from .base_server import BaseServer


class BattleServer(BaseServer):
    rounds = 8

    def __init__(self, battle_queue, pokedex):
        super(BattleServer, self).__init__(battle_queue)

        self.pokedex = pokedex

    def _request_received(self, args):
        if len(args) != 3:
            return 403, "Bad input"

        _, pid_1, pid_2 = args

        if not all([pid_1, pid_2]):
            return 403, "Bad input"

        poke_1 = self.pokedex.get_pokemon_by_id(pid_1)
        poke_2 = self.pokedex.get_pokemon_by_id(pid_2)

        if not all([poke_1, poke_2]):
            return 404, "Could not find pokemon"

        result = {'combatants': [poke_1['name'], poke_2['name']]}
        poke_1['battle_id'] = 0
        poke_2['battle_id'] = 1
        for i in range(self.rounds):
            result[i+1], term, poke_1, poke_2 = self._battle_round(
                poke_1, poke_2
            )
            if term:
                break

        return 200, result

    def _attack(self, attacker, defender):
        atk = attacker['stats']['attack']
        hp = defender['stats']['hp']
        defence = defender['stats']['defence']

        dmg = atk - defence
        hp = hp - dmg if hp - dmg > 0 else 0
        defender['stats']['hp'] = hp
        return {
            'attacker': attacker['battle_id'],
            'defender': defender['battle_id'],
            'damage': dmg,
            'hp': hp
        }, attacker, defender

    def _battle_round(self, poke_1, poke_2):
        result = []
        # who fights first?
        speed = poke_1['stats']['speed'] - poke_2['stats']['speed']

        if speed == 0:
            speed = random.random() - 0.5

        if speed > 0:
            part, poke_1, poke_2 = self._attack(poke_1, poke_2)
        elif speed < 0:
            part, poke_2, poke_1 = self._attack(poke_2, poke_1)

        result.append(part)

        if not all([poke_1['stats']['hp'], poke_2['stats']['hp']]):
            return result, True, poke_1, poke_2

        if speed > 0:
            part, poke_2, poke_1 = self._attack(poke_2, poke_1)
        else:
            part, poke_1, poke_2 = self._attack(poke_1, poke_2)
        result.append(part)

        return (
            result,
            any([poke_1['stats']['hp'] <= 0,
                 poke_2['stats']['hp'] <= 0]),
            poke_1, poke_2
        )
