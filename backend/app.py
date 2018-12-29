#!/usr/bin/env python
import pika
import os

mq_url = os.getenv("MQ_URL")

connection = pika.BlockingConnection(pika.ConnectionParameters('mq'))
channel = connection.channel()
