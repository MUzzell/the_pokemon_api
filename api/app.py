
import os
import json
from flask import Flask, abort, Response

from battle_client import BattleClient
from query_client import QueryClient

app = Flask(__name__)

mq_url = os.getenv("MQ_URL")
battle_queue = os.getenv("BATTLE_QUEUE")
query_queue = os.getenv("QUERY_QUEUE")


def _handle_request(func, ident):

    try:
        result = func(ident)
    except:
        abort(500)
    else:
        if not result or not isinstance(result, dict):
            abort(500)

        if 'code' not in result or 'data' not in result:
            abort(500)

        return Response(
            status=result['code'],
            response=json.dumps(result['data']),
            mimetype='application/json'
        )


@app.route("/id/<ident>")
def id(ident=None):
    if not ident:
        abort(403)

    with QueryClient(mq_url, query_queue) as client:
        return _handle_request(
            client.get_by_id, ident
        )


@app.route("/name/<ident>")
def name(ident=None):
    if not ident:
        abort(403)

    with QueryClient(mq_url, query_queue) as client:
        return _handle_request(
            client.get_by_name, ident
        )


@app.route("/type/<ident>")
def p_type(ident=None):
    if not ident:
        abort(403)

    with QueryClient(mq_url, query_queue) as client:
        return _handle_request(
            client.get_by_type, ident
        )


@app.route("/gen/<ident>")
def gen(ident=None):
    if not ident:
        abort(403)

    with QueryClient(mq_url, query_queue) as client:
        return _handle_request(
            client.get_by_generation, ident
        )


@app.route("/legend/<ident>")
def legend(ident=None):
    if not ident:
        abort(403)

    with QueryClient(mq_url, query_queue) as client:
        return _handle_request(
            client.get_by_legendary, ident
        )


@app.route("/stats/<ident>")
def stats(ident=None):
    if not ident:
        abort(403)

    with QueryClient(mq_url, query_queue) as client:
        return _handle_request(
            client.get_by_stats, ident
        )


@app.route("/battle/<ident>")
def battle(ident=None):
    if not ident:
        abort(403)

    with BattleClient(mq_url, battle_queue) as client:
        return _handle_request(
            client.do_battle, ident
        )
