import re

from .base_server import BaseServer

STATS_REGEX = re.compile("([a-zA-Z0-9]+)([<>=]{1,2})(\\d+)")


class QueryServer(BaseServer):

    def __init__(self, query_queue, pokedex):
        super(QueryServer, self).__init__(query_queue)
        self.query_queue = query_queue
        self.pokedex = pokedex

        self.q_func = {
            'ID': self._get_by_id,
            'NAME': self._get_by_name,
            'TYPE': self._get_by_type,
            'GEN': self._get_by_gen,
            'LEGEND': self._get_by_legendary,
            'STATS': self._get_by_stats
        }

    def _request_received(self, q_type, arg):
        try:
            result = self.q_func[q_type](arg)
        except ValueError:
            return 403, "Bad input"
        except Exception:
            return 500, "Internal server error"
        else:
            if not result:
                return 404, "Not found"
            else:
                return 200, result

    def _get_by_id(self, arg):
        arg = arg.strip()
        if not arg:
            raise ValueError("Bad input")

        return self.pokedex.get_pokemon_by_id(arg)

    def _get_by_name(self, arg):
        arg = arg.strip()
        if not arg:
            raise ValueError("Bad input")

        return self.pokedex.get_pokemon_by_name(arg)

    def _get_by_gen(self, arg):
        arg = arg.strip()
        if not arg:
            raise ValueError("Bad input")
        return self.pokedex.get_pokemon_by_generation(arg)

    def _get_by_legendary(self, arg):
        if arg.lower().strip() in ['0', 'f', 'false']:
            arg = False
        elif arg.lower().strip() in ['1', 't', 'true']:
            arg = True
        else:
            raise ValueError("Bad input")

        return self.pokedex.get_pokemon_by_legendary(arg)

    def _get_by_type(self, arg):
        p_types = [a for a in arg.split(',') if a.strip()]
        if p_types:
            return self.pokedex.get_pokemon_by_type(p_types)
        else:
            raise ValueError("Bad input")

        return None

    def _get_by_stats(self, arg):
        stats = []
        for match in STATS_REGEX.finditer(arg):
            if not match:
                continue

            stats.append((match.group(1), match.group(2), int(match.group(3))))

        if stats:
            return self.pokedex.get_pokemon_by_stats(stats)

        return None
