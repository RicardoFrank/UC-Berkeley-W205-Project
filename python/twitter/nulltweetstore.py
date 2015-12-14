from __future__ import print_function
import sys

from twitter.tweetstore import TweetStore

class NullTweetStore(TweetStore):
   """
   Throw away tweets
   """

   def __init__(self, serializer = None, tweetsPerLine=100):
      self.tweetsPerLine = tweetsPerLine
      TweetStore.__init__(self, serializer)

   def message(self, m):
      if self.tweetsPerLine is not None:
         sys.stdout.write(m)
         sys.stdout.flush()

   def close(self):
      """
      Close the store.
      """
      self.nTweets = 0
      self._closing = False

   def _logEol(self):
      self.message("%d tweets\n" % self.nTweets)

   def _logTweet(self):
      self.message('.')
      if self.tweetsPerLine is not None and self.nTweets % self.tweetsPerLine == 0:
         self._logEol()

   def write(self, s):
      '''
      We toss all tweets, so do nothing
      '''
      pass

   def writeTweet(self,  tweet):
      """
      Ignore tweet
      """
      if self._closing:
         print("writing to closing tweet store:", ''.join(traceback.format_stack()))
      self.nTweets += 1
      self.totTweets += 1
      self.totBytes += len(tweet)
      self._logTweet()
