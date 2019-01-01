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

        result = self.q_func[q_type](arg)

        if not result:
            return 404, "Not found"
        else:
            return 200, result

    def _get_by_id(self, arg):
        return self.pokedex.get_pokemon_by_id(arg)

    def _get_by_name(self, arg):
        return self.pokedex.get_pokemon_by_name(arg)

    def _get_by_gen(self, arg):
        return self.pokedex.get_pokemon_by_generation(arg)

    def _get_by_legendary(self, arg):
        return self.pokedex.get_pokemon_by_legendary(arg)

    def _get_by_type(self, arg):
        p_types = [a for a in arg.split(',') if a.strip()]
        if p_types:
            return self.pokedex.get_pokemon_by_type(p_types)

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
