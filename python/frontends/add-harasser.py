from __future__ import print_function
import sys, os, signal
import datetime, time
import re
import tweepy, json
import traceback
import argparse, pprint
import re

sys.path += [ os.getcwd() ]
from util.reentrantmethod import ReentrantMethod
from twitter.filetweetstore import FileTweetStore
from twitter.kafkatweetstore import KafkaTweetStore
from twitter.tweetwriter import TweetWriter
from twitter.tweetserializer import TweetSerializer

def interrupt(signum, frame):
   stream.disconnect()
   w.stop()

if __name__ == '__main__':

   p = argparse.ArgumentParser(
      description='Suck filtered tweets from twitter and write them into a store'
      , formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   p.add_argument('harassment', help='screen name of @harasser or a tweet id or a tweet URI')
   p.add_argument('--ntweets', dest='nTweets', type=int, default=1000
                               , help='number of recent tweets written by harasser to publish')
   p.add_argument('--max-tweets', dest='maxTweets', type=int, default=100
                                , help='max tweets written per file or line')
   kargs = p.add_argument_group('kafka', 'write tweets into Kafka store')
   portDef = 9092
   kargs.add_argument('--broker', dest='bk_endpt', nargs='?', const='localhost:9092', metavar='ENDPOINT'
                                , help='broker endpoint for kafka store')
   topicDef = 'harassing-tweets'
   kargs.add_argument('--topic', dest='topic'
                               , help='Kafka topic to which tweets are written (default: {0})'.format(topicDef))
   fargs = p.add_argument_group('file', 'write tweets into a file system store')
   patDef = 'harassment/%Y-%m-%d/%05n'
   fargs.add_argument('--pat', dest='pat'
                             , help='path name pattern to store tweets (default: {0})'.format(patDef.replace('%', '%%')))
   fargs.add_argument('--max-file-size', dest='maxSize', type=int
                                       , help='max bytes (more or less) written per tweet file')

   args = p.parse_args()

   # Handle mutually exclusive arguments;
   # ideally, argparse could handle this...
   # but its argument groups that are
   # mutually exclusive, not individual
   # arguments, so...nope.
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
      if ':' not in args.bk_endpt: args.bk_endpt += ':%s' % portDef
      st = KafkaTweetStore(endpoint = args.bk_endpt, topic = args.topic, tweetsPerLine = args.maxTweets)
   else:
      st = FileTweetStore(maxTweets = args.maxTweets, pathPattern=args.pat)
   print("tweet store created")
   s = TweetSerializer(store = st)
   st.serializer = s
   w = TweetWriter(s.write)

   # Determine what to add as harassment
   harasser = None
   harassing_tweet = None
   if args.harassment.startswith('@'):
      # A screen name
      harasser = args.harassment[1:]
   elif re.match('^http(s?)://twitter\.com/[^/]+/status/\d+$', args.harassment):
      # A URI to a tweet
      harassing_tweet = re.sub('.*/', '', args.harassment)
   elif re.match('^\d+$', args.harassment):
      # A tweet ID
      harassing_tweet = args.harassment
   else:
      # Default to a screen name
      harasser = args.harassment

   if harassing_tweet is not None:
      print("adding tweet id %s to topic '%s'" % (harassing_tweet, args.topic))
      def onetweet(id):
         yield api.get_status(id)
      iter = lambda: onetweet(harassing_tweet)
   else:
      print("adding tweets from @%s to topic '%s'" % (harasser, args.topic))
      iter = tweepy.Cursor(api.user_timeline,screen_name=harasser, count=args.nTweets).items

   try:
      for tweet in iter():
         w.on_data(tweet._json)
   except KeyboardInterrupt:
      pass
   except:
      w.on_exception(sys.exc_info()[0])

   s.end()

# vim: expandtab shiftwidth=3 softtabstop=3 tabstop=3
