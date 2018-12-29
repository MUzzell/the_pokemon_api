
import os
from flask import Flask, request

from battle_client import BattleClient

app = Flask(__name__)

mq_url = os.getenv("MQ_URL")
battle_queue = os.getenv("BATTLE_QUEUE")


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/battle", methods=['POST'])
def battle():
    data = request.json
    with BattleClient(mq_url, battle_queue) as client:
        return client.send_request(data)
