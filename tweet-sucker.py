from __future__ import print_function
import sys, os, signal
import datetime, time
import re
import tweepy, json
import traceback
import argparse, pprint
from filetweetstore import FileTweetStore
from kafkatweetstore import KafkaTweetStore
from reentrantmethod import ReentrantMethod

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
      self.store.writeTweet(json.dumps(json.loads(tweet)
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
   p.add_argument('keywords', metavar='KW', nargs='+', help='filter keywords')
   p.add_argument('--max-tweets', dest='maxTweets', type=int, default=100
                                , help='max tweets written per file or line')
   kargs = p.add_argument_group('kafka', 'write tweets into Kafka store')
   kargs.add_argument('--broker', dest='bk_endpt', nargs=1, metavar='ENDPOINT'
                                , help='broker endpoint for kafka store')
   topicDef = 'tweets'
   kargs.add_argument('--topic', dest='topic'
                               , help='Kafka topic to which tweets are written (default: {0})'.format(topicDef))
   fargs = p.add_argument_group('file', 'write tweets into a file system store')
   patDef = 'tweets/%Y-%m-%d/%05n'
   fargs.add_argument('--pat', dest='pat'
                             , help='path name pattern to store tweets (default: {0})'.format(patDef.replace('%', '%%')))
   fargs.add_argument('--max-file-size', dest='maxSize', type=int
                                       , help='max bytes (more or less) written per tweet file')

   args = p.parse_args()
   pp = pprint.PrettyPrinter(indent=4)
   for x in [args, kargs, fargs]:
      pp.pprint(x)

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

   # Handle signals
   signal.signal(signal.SIGINT, interrupt)
   signal.signal(signal.SIGTERM, interrupt)

   api = tweepy.API(auth_handler=auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
   print("tweepy API created")
   if kafka:
      st = KafkaTweetStore(endpoint = args.bk_endpt[0], topic = args.topic, tweetsPerLine = args.maxTweets)
   else:
      st = FileTweetStore(maxTweets = args.maxTweets, pathPattern=args.pat)
   print("tweet store created")
   s = TweetSerializer(store = st)
   st.serializer = s
   w = TweetWriter(s.write)
   stream = tweepy.Stream(auth, w)
   print("twitter stream created")

   # filter stream according to argv, in a separate thread
   stream.filter(track=sys.argv, async=True)
   print("filtering tweets")

   # Pass the time, waiting for an interrupt
   while not w.stopped:
      signal.pause()
      print("signalled")
   stream.disconnect()
   stream._thread.join()
   s.end()

# vim: expandtab shiftwidth=3 softtabstop=3 tabstop=3
