from __future__ import print_function
import sys

from twitter.tweetstore import TweetStore
from classifer.remote import RemoteTweetClassifier

class ClassifierTweetStore(TweetStore):
   """
   Send tweets to a classifier
   """

   def __init__(self, endpoint, classify=True, serializer = None, tweetsPerLine=100):
      """
      """
      self.c = RemoteTweetClassifier(endpoint)
      self.send = c.isHarassingTweet if classify else c.addHarassingTweet
      self.tweetsPerLine = tweetsPerLine
      TweetStore.__init__(self, serializer)
      print("created CTS, tweetsPerLine %d" % self.tweetsPerLine)

   def message(self, m):
      if self.tweetsPerLine is not None:
         sys.stdout.write(m)
         sys.stdout.flush()

   def close(self):
      """
      Close the store.
      """
      if self.c is None:
         return
      self._closing = True
      self._logEol()
      self.serializer.closing()
      self.nTweets = 0
      self._closing = False
      self.c = None

   def _logEol(self):
      if self.c is not None:
	  self.message("%d tweets\n" % self.nTweets)

   def _logTweet(self):
      self.message('.')
      if self.tweetsPerLine is not None and self.nTweets % self.tweetsPerLine == 0:
         self._logEol()

   def write(self, s):
      """
      write() makes no sense for a classifier
      where messages are atomic units and
      so don't require bytes to mark tweets
      """
      pass

   def writeTweet(self,  tweet):
      """
      Send tweets to a classifier
      """
      if self._closing:
         print("writing to closing tweet store:", ''.join(traceback.format_stack()))
      self.nTweets += 1
      self.totTweets += 1
      self.totBytes += len(tweet)
      self.send(tweet)
      self._logTweet()
