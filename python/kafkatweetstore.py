from __future__ import print_function
from kafka import KafkaClient, SimpleProducer
import sys

class KafkaTweetStore(object):
   """
   Store tweets in a Kafka log
   """
   serializer = None
   _closing = False
   client = None
   producer = None
   topic = None
   nTweets = 0
   tweetsPerLine = None


   def __init__(self, serializer = None, endpoint = None, topic = None, tweetsPerLine = None):
      """
      """
      self.serializer = serializer
      self.client = KafkaClient(endpoint)
      self.producer = SimpleProducer(self.client, async=True)
      self.topic = topic
      self.tweetsPerLine = tweetsPerLine
      print("created KTS, tweetsPerLine %d" % self.tweetsPerLine)

   def message(self, m):
      if self.tweetsPerLine is not None:
         sys.stdout.write(m)
         sys.stdout.flush()

   def close(self):
      """
      Close the store.
      """
      if self.client is None:
         return
      self._closing = True
      self._logEol()
      self.serializer.closing()
      self.client.close()
      self.client = None
      self.nTweets = 0
      self._closing = False

   def _logEol(self):
      if self.client is not None:
	  self.message("%d tweets\n" % self.nTweets)

   def _logTweet(self):
      self.message('.')
      if self.tweetsPerLine is not None and self.nTweets % self.tweetsPerLine == 0:
         self._logEol()

   def write(self, s):
      """
      write() makes no sense for Kafka,
      where messages are atomic units and
      so don't require bytes to mark tweets
      """
      pass

   def writeTweet(self,  tweet):
      """
      Write a tweet to the store.
      """
      if self._closing:
         print("writing to closing tweet store:", ''.join(traceback.format_stack()))
      self.nTweets += 1
      self.producer.send_messages(self.topic, tweet)
      self._logTweet()
