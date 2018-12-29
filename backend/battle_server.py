import pika
import os


def setup(channel):
    battle_queue = os.getenv("BATTLE_QUEUE")
    channel.queue_declare(queue=battle_queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(handle_request, queue=battle_queue)


def handle_request(ch, method, props, body):
    print("Got battle request")
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(
                                    correlation_id=props.correlation_id
                                ),
                     body="yes")
    ch.basic_ack(delivery_tag=method.delivery_tag)
