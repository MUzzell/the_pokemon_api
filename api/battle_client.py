
from base_client import BaseClient, format_query


class BattleClient(BaseClient):
    retries = 3

    def do_battle(self, ident):
        return self._send_request(format_query("BATTLE", ident))
