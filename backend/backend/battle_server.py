import pika


class BattleServer(object):

    def __init__(self, battle_queue, pokedex):
        self.battle_queue = battle_queue#
        self.pokedex = pokedex

    def setup(self, channel):
        channel.queue_declare(queue=self.battle_queue)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.handle_request, queue=self.battle_queue)

    def handle_request(self, ch, method, props, body):
        print("Got battle request")
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(
                                        correlation_id=props.correlation_id
                                    ),
                         body="yes")
        ch.basic_ack(delivery_tag=method.delivery_tag)
