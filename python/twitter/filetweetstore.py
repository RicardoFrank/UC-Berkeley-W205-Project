from __future__ import print_function
import sys, os, signal
import datetime, time
import re
import tweepy, json
import traceback
from util.reentrantmethod import ReentrantMethod
from twitter.tweetstore import TweetStore

class FileTweetStore(TweetStore):
   """
   Store tweets in files according to a policy.
   """
   _substRe = re.compile('(%\d*n)')

   B = 1
   KB = 1000 * B
   MB = 1000 * KB
   GB = 1000 * MB
   TB = 1000 * GB

   def __init__(self, serializer = None, pathPattern = "%Y-%m-%d/tweets-%05n", maxTweets = -1, maxSize = -1):
      """
      Set policy of how tweets are stored.

      maxTweets   - max # of tweets per file
      maxSize     - tweets will be written to a new file
                    once current one exceeds this limit in bytes
      pathPattern - a pattern for how files containing tweets
                    will be named.  can contain %-directives.
                    %n indicate a file number, all others are
                    as in strftime, which see. a pattern like
                    "%Y-%m-%d/%04n" will put tweets in a file
                    named 2015-01-01/0001.  As time passes,
                    those files will move to 2015-01-02.
      """
      TweetStore.__init__(self, serializer)
      self.pathPattern = pathPattern
      self.nFiles = 0
      self.file = None
      self._path = None
      self.maxTweets = maxTweets
      self.maxSize = maxSize
      self.once = True if '%n' not in self.pathPattern else None
      ReentrantMethod(self, self.close)

   def _substPctN(self, pat):
      m = self._substRe.search(pat)
      if m == None:
         return pat
      s = m.group().replace('n', 'd') % self.nFiles
      return self._substRe.sub(s, pat)

   def _makePath(self, n):
      pat = self._substPctN(self.pathPattern)
      path = time.strftime(pat)
      return path

   def _nextPath(self):
      if self.once is not None:
	 if not self.once:
	    return
	 self.once = False
	 self._path = self._makePath(self.nFiles)
	 return

      path = self._path
      while path == None or os.path.exists(path):
         self.nFiles += 1
         path = self._makePath(self.nFiles)
      self._path = path

   def _newFile(self):
      self.close()
      self._nextPath()
      d = os.path.dirname(self._path)
      if not os.path.exists(d):
         os.makedirs(d)
      print("new file: ", self._path)
      self.file = open(self._path, 'w')

   def close(self):
      """
      Close the store.

      A subsequent write to the store will re-open it.
      """
      if self.file == None:
         return
      self._closing = True
      sys.stdout.write("\n")
      self.serializer.closing()
      self.file.close()
      if self.nTweets == 0:
         # no tweets => don't need this file
         os.remove(self._path)
         self.nFiles -= 1
      self.file = None
      self.nTweets = 0
      self._closing = False

   def write(self, s):
      """
      Write bytes to a tweet store.

      Typically, these bytes have to do with
      serialization.  Write tweets using the
      writeTweet() method.
      """
      if self.file == None:
         self._newFile()
      self.file.write(s)

   def writeTweet(self,  tweet):
      """
      Write a tweet to the store.
      """
      if self._closing:
         print("writing to closing tweet store:", ''.join(traceback.format_stack()))
      self.nTweets += 1
      self.totTweets += 1
      self.totBytes += len(tweet)
      sys.stdout.write('.')
      sys.stdout.flush()
      self.write(tweet)
      if self.maxTweets >= 0 and self.nTweets == self.maxTweets \
         or self.maxSize >= 0 and self.file.tell() >= self.maxSize \
         or self._path != self._makePath(self.nFiles):
         print("%d tweets, max %d; %d bytes, max %d" %
               (self.nTweets, self.maxTweets, self.file.tell(), self.maxSize))
         self.close()
      self._closing = False
