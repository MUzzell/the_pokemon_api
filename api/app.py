
import os
from flask import Flask, request, abort, Response

from battle_client import BattleClient
from query_client import QueryClient

app = Flask(__name__)

mq_url = os.getenv("MQ_URL")
battle_queue = os.getenv("BATTLE_QUEUE")
query_queue = os.getenv("QUERY_QUEUE")


@app.route("/id/<ident>")
def id(ident=None):
    if not ident:
        abort(404)
    print("Sending ID request")
    with QueryClient(mq_url, query_queue) as client:
        return Response(
            response=client.get_by_id(ident),
            status=200,
            mimetype="application/json"
        )


@app.route("/name/<ident>")
def name(ident=None):
    if not ident:
        abort(404)
    with QueryClient(mq_url, query_queue) as client:
        return Response(
            response=client.get_by_name(ident),
            status=200,
            mimetype="application/json"
        )


@app.route("/battle", methods=['POST'])
def battle():
    data = request.json
    with BattleClient(mq_url, battle_queue) as client:
        return client.send_request(data)
