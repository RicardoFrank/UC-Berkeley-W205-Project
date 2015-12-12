from __future__ import print_function
import sys, os, argparse
import json, re
import xmlrpclib
import pprint
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

sys.path += [ os.getcwd() ]
from classifier.rand import RandomTweetClassifier
from classifier.key_word import KeywordTweetClassifier
from classifier.remote import RemoteTweetClassifier
from util.singleton import Singleton

if __name__ == "__main__":
   p = argparse.ArgumentParser(
      description='Spark job to monitor tweets and classify them as harassers'
      , formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   p.add_argument('--broker', dest='bk_endpt', required=True, metavar='ENDPOINT'
		  , help='broker endpoint for kafka store')
   p.add_argument('--model-path', dest='modelPath', metavar='MODEL_PATH', default='file:///tmp/model'
		  , help="path to read/store tweet classifier's model")
   args = p.parse_args()

   sc = SparkContext("local[2]", "block-harassers")
   ssc = StreamingContext(sc, 5)
   ssc.checkpoint("file:///tmp/checkpointing")

   pp = pprint.PrettyPrinter(indent=4)
   pp.pprint(args.bk_endpt)

   def preprocess(rdd):
      """
      Pre-process tweets in rdd so they'll be
      suitable for use in the downstream topology
      """
      return rdd.map(
         # xform to dicts
         lambda js: json.loads(js[1])
      ).filter(
         # english only
         lambda tweet: 'lang' in tweet and tweet['lang'] == 'en'
      ).map(
      # pluck out tweet's text & downcase it
         lambda tweet: (tweet['user']['screen_name'], tweet['text'].lower())
      ).map(
         # kill punctuation, except for @mentions and #hashtags and spaces
         lambda t: (t[0], re.sub("[^\w\s@#]+", '', t[1]))
      ).map(
         # pprint() can only handle ascii, it seems
         lambda t: [ _.encode('ascii','ignore') for _ in t ]
      )

   tweets = KafkaUtils.createDirectStream(ssc, [ 'tweets' ], { "metadata.broker.list": args.bk_endpt })
   harassing_tweets = KafkaUtils.createDirectStream(ssc, [ 'harassing-tweets' ], { "metadata.broker.list": args.bk_endpt })

   c = Singleton.get('tweetClassifier', lambda: RandomTweetClassifier(p=0.01))
   #c = Singleton.get('tweetClassifier', lambda: KeywordTweetClassifier())
   #c = Singleton.get('tweetClassifier', lambda: RemoteTweetClassifier('http://localhost:6666'))
   #c = RandomTweetClassifier(p=1.0)
   c = RemoteTweetClassifier('http://localhost:6666')

   tweets.count().pprint()
   #def isHarassingTweet(txt):
      #class px:
         #proxy = None
         #@classmethod
         #def p(self):
            #if self.proxy is None: self.proxy = xmlrpclib.ServerProxy("http://localhost:6666", allow_none = True)
            #return self.proxy
      #return px.p().isHarassingTweet(txt)

   #preprocess(tweets).filter(
      #lambda t: isHarassingTweet(t[1])
   #).pprint()
   preprocess(tweets).filter(
      lambda t: [ print("filtering - @%s: %s" % (t[0], t[1])), c.isHarassingTweet(t[1])][1]
   ).pprint()

   harassing_tweets.count().pprint()
   #def addHarassingTweets(iter):
       #proxy = xmlrpclib.ServerProxy("http://localhost:6666/")
       #for t in iter:
           #proxy.addHarassingTweet(t[1])
       #proxy('close')()

   #preprocess(harassing_tweets).foreachRDD(
      #lambda rdd: rdd.foreachPartition(addHarassingTweets)
   #)
   preprocess(harassing_tweets).foreachRDD(
      lambda rdd: rdd.foreach(lambda t: [ print("   adding - @%s: %s" % (t[0], t[1])), c.addHarassingTweet(t[1])][1])
                             #lambda t: [ print("filtering - @%s: %s" % (t[0], t[1])), c. isHarassingTweet(t[1])][1]
   )


   ssc.start()
   ssc.awaitTermination()
# vim: expandtab shiftwidth=3 softtabstop=3 tabstop=3
