import kafka as k
# There's a bug in kafka's SimpleConsumer
# (cf https://github.com/dpkp/kafka-python/issues/311).
# Use pykafka's instead.
import pykafka as pk

class KafkaTransceiver(object):
    def __init__(self, endpoint, group='harasser-blocker'):
	self.kclient = None
	self.pkclient = None
	self.producer = None
	self.endpt = endpoint
	self.consumers = {}
	self.group = group

    def xmit(self, topic, msg):
	if self.kclient is None: self.kclient = k.KafkaClient(self.endpt)
	if self.producer is None: self.producer = k.SimpleProducer(self.kclient, async=True)
	self.producer.send_messages(topic, msg)

    def recv(self, topic):
	if self.pkclient is None: self.pkclient = pk.KafkaClient(self.endpt)
	if topic not in self.consumers:
	    self.consumers[topic] = self.pkclient.topics[topic].get_simple_consumer(consumer_group=self.group, auto_commit_enable=True)
	return self.consumers[topic].consume(block=True).value

    def close(self):
	if self.producer is not None:
	    self.producer.stop()
	for t in self.consumers:
	    self.consumers[t].stop()
	if self.kclient is not None:
	    self.kclient.close()
	self.consumers = {}
	self.producer = \
	self.kclient = \
	self.pkclient = \
	None
