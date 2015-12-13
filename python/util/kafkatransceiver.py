from kafka import KafkaClient, SimpleProducer, SimpleConsumer

class KafkaTransceiver(object):
    def __init__(self, endpoint):
	self.client = None
	self.producer = None
	self.endpt = endpoint
	self.consumers = {}

    def xmit(self, topic, msg):
	if self.client is None: self.client = KafkaClient(self.endpt)
	if self.producer is None: self.producer = SimpleProducer(self.client, async=True)
	self.producer.send_messages(topic, msg)

    def recv(self, topic):
	if self.client is None: self.client = KafkaClient(self.endpt)
	if topic not in self.consumers: self.consumers[topic] = SimpleConsumer(self.client, group='', topic=topic)
	return self.consumers[topic].get_message(timeout=None)

    def close(self):
	if self.producer is not None:
	    self.producer.stop()
	for t in self.consumers:
	    self.consumers[t].commit()
	if self.client is not None:
	    self.client.close()
	self.producer = \
	self.consumer = \
	self.client = None

