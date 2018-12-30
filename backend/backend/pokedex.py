
import redis
import json

POKEMON_ID_KEY = "pokemon:id:"
POKEMON_NAME_KEY = "pokemon:name:"
POKEMON_TYPE_KEY = "pokemon:type:"
POKEMON_STATS_KEY = "pokemon:stats:"
POKEMON_LEGEND_KEY = "pokemon:legendary:"
POKEMON_GEN_KEY = "pokemon:gen:"


def _build_key(base, ident):
    return "{}{}".format(base, ident)


class Pokedex(object):

    def __init__(self, redis_url):
        self.redis = redis.Redis.from_url(url=redis_url)

    def import_data(self, data_file):

        with open(data_file, 'r') as f:
            f.readline()  # not interested in first line

            # id,Name,Type 1,Type 2,Total,HP,Attack,Defense,Sp.Atk,Sp.Def,Speed,Generation,Legendary
            for line in f:
                data = line.split(',')
                pokemon = {
                    'id': data[0],
                    'name': data[1],
                    'type': [data[2], data[3]],
                    'stats': {
                        'total': int(data[4]),
                        'hp': int(data[5]),
                        'attack': int(data[6]),
                        'defense': int(data[7]),
                        'sp.atk': int(data[8]),
                        'sp.def': int(data[9]),
                        'speed': int(data[10])
                    },
                    'gen': int(data[11]),
                    'legendary': bool(data[12])
                }
                self._import_pokemon(pokemon)

    def _reset_lists(self):
        def delete_list(redis, key):
            while redis.llen(key) > 0:
                redis.ltrim(key, 0, -99)

        for key in self.redis.keys(_build_key(POKEMON_TYPE_KEY, '*')):
            delete_list(self.redis, key)

        for key in self.redis.keys(_build_key(POKEMON_STATS_KEY, '*')):
            delete_list(self.redis, key)

        for key in self.redis.keys(_build_key(POKEMON_GEN_KEY, '*')):
            delete_list(self.redis, key)

        for key in self.redis.keys(_build_key(POKEMON_LEGEND_KEY, '*')):
            delete_list(self.redis, key)

    def _import_pokemon(self, pokemon):
        p_id = pokemon['id']
        if self.redis.get(_build_key(POKEMON_ID_KEY, pokemon['id'])):
            print("Pokemon id: {} ({}) already in pokedex, skipping".format(
                p_id, pokemon['name'])
            )
            return  # ASSUMPTION: pokemon details don't change

        self.redis.set(
            _build_key(POKEMON_ID_KEY, p_id), json.dumps(pokemon)
        )
        self.redis.set(
            _build_key(POKEMON_NAME_KEY, pokemon['name']), p_id
        )
        self.redis.lpush(
            _build_key(POKEMON_GEN_KEY, pokemon['gen']), p_id
        )
        self.redis.lpush(
            _build_key(POKEMON_LEGEND_KEY, pokemon['legendary']), p_id
        )
        for p_type in pokemon['type']:
            if p_type:
                self.redis.lpush(
                    _build_key(POKEMON_TYPE_KEY, p_type), p_id
                )
        for stat, val in pokemon['stats'].items():
            self.redis.lpush(
                _build_key(POKEMON_STATS_KEY, stat),
                "{}:{}".format(val, p_id)
            )

    def get_pokemon_by_id(self, p_id):
        return self.redis.get(_build_key(POKEMON_ID_KEY, p_id))

    def get_pokemon_by_name(self, name):
        ids = self.redis.scan(match=_build_key(POKEMON_NAME_KEY, name))
        if not ids:
            return []
        return [self.get_pokemon_by_id(p_id) for p_id in ids]

    def get_pokemon_by_type(self, p_type):
        pass

    def get_pokemon_by_stats(self, stats):
        pass
