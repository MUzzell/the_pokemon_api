
from base_client import BaseClient, format_query


class QueryClient(BaseClient):

    def get_by_id(self, ident):
        return self._send_request(format_query("ID", ident))

    def get_by_name(self, name):
        return self._send_request(format_query("NAME", name))

    def get_by_type(self, p_type):
        return self._send_request(format_query("TYPE", p_type))

    def get_by_generation(self, gen):
        return self._send_request(format_query("GEN", gen))

    def get_by_legendary(self, is_legend):
        return self._send_request(format_query("LEGEND", is_legend))

    def get_by_stats(self, stats):
        return self._send_request(format_query("STATS", stats))
