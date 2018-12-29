#!/usr/bin/env python
import pika
import os
import time

from .battle_server import BattleServer
from .query_server import QueryServer


def setup(connection):
    battle_server = BattleServer(os.getenv("BATTLE_QUEUE"))
    query_server = QueryServer(os.getenv("QUERY_QUEUE"))

    print("Setting up channel")
    channel = connection.channel()
    battle_server.setup(channel)
    query_server.setup(channel)

    print("Start consuming")
    channel.start_consuming()
    print("app closing down")


mq_url = os.getenv("MQ_URL")
retries = 3

print("Connecting to MQ")
while retries:
    try:
        connection = pika.BlockingConnection(pika.URLParameters(mq_url))
        setup(connection)
        break
    except pika.exceptions.ConnectionClosed:
        if not retries:
            print("Giving up connection after 3 attempts")
            raise
        print("Could not connect to MQ, retrying")
        retries -= 1
        time.sleep(3)
