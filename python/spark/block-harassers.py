from __future__ import print_function
import sys, os, argparse
import json, re
import xmlrpclib
import tweepy
import pprint
from gensim.parsing.preprocessing import remove_stopwords
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils, TopicAndPartition

sys.path += [ os.getcwd() ]
from classifier.rand import RandomTweetClassifier
from classifier.key_word import KeywordTweetClassifier
from classifier.remote import RemoteTweetClassifier
from util.kafkatransceiver import KafkaTransceiver

if __name__ == "__main__":
   p = argparse.ArgumentParser(
      description='Spark job to monitor tweets and classify them as harassers'
      , formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   p.add_argument('--broker', dest='bk_endpt', required=True, metavar='ENDPOINT'
		  , help='broker endpoint for kafka store')
   p.add_argument('--classifier', dest='cf_endpt', metavar='ENDPOINT'
        , default='http://localhost:6666'
		  , help="endpoint for remote classifier")
   p.add_argument('--reload-harassment', dest='reload', action='store_true'
		  , help="reload all harassing tweets, presumably to rebuild the classifier's model")
   args = p.parse_args()

   execfile('./creds.py')
   auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
   auth.set_access_token(access_token, access_token_secret)
   api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
   me = api.me().id_str

   sc = SparkContext("local[2]", "block-harassers")
   ssc = StreamingContext(sc, 5)
   ssc.checkpoint("file:///tmp/checkpointing")

   pp = pprint.PrettyPrinter(indent=4)
   pp.pprint(args)

   def preprocess(rdd):
      """
      Pre-process tweets in rdd so they'll be
      suitable for use in the downstream topology
      """
      return rdd.map(
         # xform json into dicts
         lambda js: json.loads(js[1])
      ).filter(
         # analyze only tweets from users (skip "delete" messages, eg)
         lambda tweet: 'user' in tweet
      ).filter(
         # don't analyze our own tweets
         lambda tweet: tweet['user']['id_str'] != me
      ).filter(
         # english only
         lambda tweet: 'lang' in tweet and tweet['lang'] == 'en'
      ).map(
         # pluck out tweet's author & text & downcase tweet text
         lambda tweet: (tweet['user']['screen_name'], tweet['text'].lower())
      ).map(
         # kill punctuation, except for @mentions and #hashtags and spaces
         lambda t: (t[0], re.sub("[^\w\s@#]+", '', t[1]))
      ).map(
         # add text w/ stop words removed
         lambda t: (t[0], t[1], remove_stopwords(t[1]))
      ).map(
         # pprint() can only handle ascii, it seems
         lambda t: [ _.encode('ascii','ignore') for _ in t ]
      )

   tweets = KafkaUtils.createDirectStream(ssc, [ 'tweets' ], { "metadata.broker.list": args.bk_endpt })

   offset = None if not args.reload else { TopicAndPartition('harassing-tweets', 0): 0L }
   harassing_tweets = KafkaUtils.createDirectStream(ssc, [ 'harassing-tweets' ]
                                                    , { "metadata.broker.list": args.bk_endpt }
                                                    , fromOffsets = offset)

   c = RemoteTweetClassifier(args.cf_endpt)
   k = KafkaTransceiver(args.bk_endpt)

   tweets.count().pprint()
   preprocess(tweets).filter(
      lambda t: c.isHarassingTweet(t[2])
   ).map(
      lambda t: (k.xmit('harassers', json.dumps({ "author": t[0], "text": t[1] })), t)[1]
   ).pprint()

   harassing_tweets.count().pprint()
   preprocess(harassing_tweets).foreachRDD(
      lambda rdd: rdd.foreach(lambda t: (pp.pprint(t), c.addHarassingTweet(t[2])))
   )

   ssc.start()
   ssc.awaitTermination()
# vim: expandtab shiftwidth=3 softtabstop=3 tabstop=3
