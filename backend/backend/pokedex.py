
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


def _check_attr(entry, t, exp):
    if not entry:
        raise exp
    if t == bool:
        if entry.lower().strip() in ['f', 'false', '0']:
            return False
        elif entry.lower().strip() in ['t', 'true', '1']:
            return True
        else:
            raise exp
    if t == str:
        return entry
    entry = entry.strip()
    try:
        return t(entry)
    except ValueError:
        raise exp


class Pokedex(object):

    def __init__(self, redis_url):
        self.redis = redis.Redis.from_url(url=redis_url)

    def import_data(self, data_file):

        with open(data_file, 'r') as f:
            f.readline()  # not interested in first line

            # id,Name,Type 1,Type 2,Total,HP,Attack,Defense,Sp.Atk,Sp.Def,Speed,Generation,Legendary
            l = 2
            for line in f:
                try:
                    pokemon = self._parse_pokemon_line(line)
                except ValueError as ve:
                    print("Invalid entry at line {}: {}".format(l, ve.message))
                else:
                    self._import_pokemon(pokemon)
                    l += 1

    def _parse_pokemon_line(self, line):

        def check_type(type_a, type_b):
            if not type_a:
                raise ValueError("Invalid Type 1")

            if type_b:
                return [type_a, type_b]

            return [type_a]

        data = line.split(',')
        if len(data) != 13:
            raise ValueError(
                "Not enough attributes"
            )
        return {
            'id': _check_attr(data[0], str, ValueError("No Id")),
            'name': _check_attr(data[1], str, ValueError("No name")),
            'type': check_type(data[2], data[3]),
            'stats': {
                'total': _check_attr(data[4], int, ValueError("Invalid total")),
                'hp': _check_attr(data[5], int, ValueError("Invalid HP")),
                'attack': _check_attr(data[6], int, ValueError("Invalid attack")),
                'defense': _check_attr(data[7], int, ValueError("Invalid defense")),
                'sp.atk': _check_attr(data[8], int, ValueError("Invalid sp.atk")),
                'sp.def': _check_attr(data[9], int, ValueError("Invalid sp.def")),
                'speed': _check_attr(data[10], int, ValueError("Invalid speed"))
            },
            'gen': _check_attr(data[11], int, ValueError("Invalid generation Id")),
            'legendary': _check_attr(data[12], bool, ValueError("Invalid legendary"))
        }

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
                    _build_key(POKEMON_TYPE_KEY, p_type.lower().strip()), p_id
                )
        for stat, val in pokemon['stats'].items():
            self.redis.lpush(
                _build_key(POKEMON_STATS_KEY, stat.lower().strip()),
                "{}:{}".format(val, p_id)
            )

    def get_pokemon_by_id(self, p_id):
        result = self.redis.get(
            _build_key(POKEMON_ID_KEY, p_id)
        )
        if not result:
            return None
        return json.loads(result.decode('ASCII'))

    def get_pokemon_by_name(self, name):
        ids = [self.redis.get(ident).decode("ASCII")
               for ident in self.redis.scan_iter(
            match=_build_key(POKEMON_NAME_KEY, name)
        )]
        if not ids:
            return []
        return [self.get_pokemon_by_id(p_id) for p_id in ids]

    def get_pokemon_of_type(self, p_type):
        key = _build_key(POKEMON_TYPE_KEY, p_type.lower().strip())
        ids = self.redis.lrange(key, 0, -1)
        if not ids:
            return []

        return [self.get_pokemon_by_id(p_id.decode('ASCII')) for p_id in ids]

    def get_pokemon_by_type(self, p_types):
        result = []
        for p_type in p_types:
            result.append(self.get_pokemon_of_type(p_type))

        if not result or not any(result):
            return []

        ids = [{a['id'] for a in b} for b in result]

        ids = ids[0].intersection(*ids[1:])
        return [a for a in result[0] if a['id'] in ids]

    def get_pokemon_by_generation(self, gen):
        key = _build_key(POKEMON_GEN_KEY, gen)
        ids = self.redis.lrange(key, 0, -1)
        if not ids:
            return []

        return [self.get_pokemon_by_id(p_id.decode('ASCII')) for p_id in ids]

    def get_pokemon_by_legendary(self, is_legend):
        key = _build_key(POKEMON_LEGEND_KEY, is_legend)
        ids = self.redis.lrange(key, 0, -1)
        if not ids:
            return []

        return [self.get_pokemon_by_id(p_id.decode('ASCII')) for p_id in ids]

    def get_pokemon_by_stats(self, stats):
        pass
