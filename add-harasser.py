from __future__ import print_function
import sys, os, signal
import datetime, time
import re
import tweepy, json
import traceback
import argparse, pprint
from kafkatweetstore import KafkaTweetStore

class ReentrantMethod(object):
   """
   Make a given object's method be re-entrant.
   """

   orig_meth = None
   obj = None
   def __init__(self, obj, meth):
      self.orig_meth = meth
      self.obj = obj
      setattr(self.obj, self.orig_meth.func_name, self._wrap)
   def _noop(self, *args, **kwargs):
      pass
   def _wrap(self, *args, **kwargs):
      setattr(self.obj, self.orig_meth.func_name, self._noop)
      self.orig_meth(*args, **kwargs)
      setattr(self.obj, self.orig_meth.func_name, self._wrap)


class TweetStore(object):
   """
   Store tweets according to a policy.
   """
   serializer = None
   maxTweets = -1
   maxSize = -1
   nTweets = 0
   nFiles = 0
   pathPattern = None
   file = None
   _closing = False
   _path = None
   _substRe = re.compile('(%\d*n)')

   B = 1
   KB = 1000 * B
   MB = 1000 * KB
   GB = 1000 * MB
   TB = 1000 * GB

   def __init__(self, serializer = None, pathPattern = "%Y-%m-%d/tweets-%05n", maxTweets = None, maxSize = None):
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
      self.serializer = serializer
      self.pathPattern = pathPattern
      if maxTweets != None:
         self.maxTweets = maxTweets
      if maxSize != None:
         self.maxSize = maxSize
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

class TweetSerializer(object):
   first = None
   ended = None
   store = None

   def __init__(self, store = None):
      self.store = store
      self.ended = True
      ReentrantMethod(self, self.end)

   def start(self):
      self.store.write("[\n")
      self.first = True
      self.ended = False

   def end(self):
      if not self.ended:
         self.store.write("\n]\n")
         self.store.close()
         self.first = False
         self.ended = True

   def write(self, tweet):
      if self.ended:
         self.start()
      if not self.first:
         self.store.write(",\n")
      self.first = False
      self.store.writeTweet(json.dumps(tweet
                                       , indent=4
                                       , separators=(',', ': ')).encode('utf8'))

   def closing(self):
      self.end()

class TweetWriter(tweepy.StreamListener):
   write = None
   stopped = False

   def __init__(self, serializer = None):
      self.write = serializer

   def on_data(self, data):
      if not self.stopped:
         self.write(data)
      return not self.stopped

   def on_disconnect(self, notice):
      print("disconnected", file=sys.stderr)
      self.stop()
      os.kill(os.getpid(), signal.SIGTERM)
      return False

   def on_error(self, status):
      print("error from tweet stream: ", status, file=sys.stderr)
      self.stop()
      os.kill(os.getpid(), signal.SIGTERM)
      return False

   def on_exception(self, e):
      print("exception: ", e)
      traceback.print_exc()

   def stop(self):
      self.stopped = True

def interrupt(signum, frame):
   stream.disconnect()
   w.stop()

if __name__ == '__main__':

   p = argparse.ArgumentParser(
      description='Suck filtered tweets from twitter and write them into a store'
      , formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   p.add_argument('harasser', help='screen name of harasser')
   p.add_argument('--ntweets', dest='nTweets', type=int, default=1000
                               , help='number of recent tweets written by harasser to publish')
   p.add_argument('--max-tweets', dest='maxTweets', type=int, default=100
                                , help='max tweets written per file or line')
   kargs = p.add_argument_group('kafka', 'write tweets into Kafka store')
   kargs.add_argument('--broker', dest='bk_endpt', nargs=1, metavar='ENDPOINT'
                                , help='broker endpoint for kafka store')
   topicDef = 'harassing-tweets'
   kargs.add_argument('--topic', dest='topic'
                               , help='Kafka topic to which tweets are written (default: {0})'.format(topicDef))
   fargs = p.add_argument_group('file', 'write tweets into a file system store')
   patDef = 'harassers/%Y-%m-%d/%05n'
   fargs.add_argument('--pat', dest='pat'
                             , help='path name pattern to store tweets (default: {0})'.format(patDef.replace('%', '%%')))
   fargs.add_argument('--max-file-size', dest='maxSize', type=int
                                       , help='max bytes (more or less) written per tweet file')

   args = p.parse_args()

   # Handle mutually exclusive arguments;
   # ideally, argparse could handle this...
   # but it's argument groups that are
   # mutually exclusive, not individual
   # arguments, so...nope.
   # is to use a file system store, y
   kafka = args.bk_endpt or args.topic
   file = args.pat or args.maxSize
   if kafka and file:
      print("can't mix both Kafka log and file store options\n",
            p.format_usage(), file=sys.stderr)
      exit(1)
   # We're forced to handle defaults
   # ourselves, since we must detect
   # mutually exclusive groups ourselves
   if args.pat is None:
      args.pat = patDef
   if args.topic is None:
      args.topic = topicDef

   # Bring in twitter creds; this file is *not*
   # in source code control; you've got to provide
   # it yourself
   execfile("./creds.py");

   auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
   auth.set_access_token(access_token, access_token_secret)

   ## Handle signals
   #signal.signal(signal.SIGINT, interrupt)
   #signal.signal(signal.SIGTERM, interrupt)

   api = tweepy.API(auth_handler=auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
   print("tweepy API created")
   if kafka:
      st = KafkaTweetStore(endpoint = args.bk_endpt[0], topic = args.topic, tweetsPerLine = args.maxTweets)
   else:
      st = TweetStore(maxTweets = args.maxTweets, pathPattern=args.pat)
   print("tweet store created")
   s = TweetSerializer(store = st)
   st.serializer = s
   w = TweetWriter(s.write)

   try:
      for tweet in tweepy.Cursor(api.user_timeline,screen_name=args.harasser, count=args.nTweets).items():
         w.on_data(tweet._json)
   except KeyboardInterrupt:
      pass
   except:
      w.on_exception(sys.exc_info()[0])

   s.end()

# vim: expandtab shiftwidth=3 softtabstop=3 tabstop=3
