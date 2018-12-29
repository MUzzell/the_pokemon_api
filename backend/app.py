#!/usr/bin/env python
import pika
import os
import time

from battle import setup as battle_setup
from query import setup as query_setup

mq_url = os.getenv("MQ_URL")

retries = 3

print("Connecting to MQ")
while retries:
    try:
        connection = pika.BlockingConnection(pika.URLParameters(mq_url))
        break
    except pika.exceptions.ConnectionClosed:
        if not retries:
            print("Giving up connection after 3 attempts")
            raise
        print("Could not connect to MQ, retrying")
        retries -= 1
        time.sleep(2)

channel = connection.channel()
print("Setting up channel")
battle_setup(channel)
query_setup(channel)

print("Start consuming")
channel.start_consuming()
print("app closing down")
