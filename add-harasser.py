from __future__ import print_function
import sys, os, signal
import datetime, time
import re
import tweepy, json
import traceback
import argparse, pprint
from reentrantmethod import ReentrantMethod
from filetweetstore import FileTweetStore
from kafkatweetstore import KafkaTweetStore
from tweetwriter import TweetWriter


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
      st = FileTweetStore(maxTweets = args.maxTweets, pathPattern=args.pat)
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
