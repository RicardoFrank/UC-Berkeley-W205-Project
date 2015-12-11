import sys, os, argparse
import json, re
import pprint
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

sys.path += [ os.getcwd() ]
from classifier.rand import RandomTweetClassifier
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
   ssc = StreamingContext(sc, 10)
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
         lambda tweet: tweet['lang'] == 'en'
      ).map(
      # pluck out tweet's text & downcase it
         lambda tweet: tweet['text'].lower()
      ).map(
         # kill punctuation, except for @mentions and #hashtags and spaces
         lambda txt: re.sub("[^\w\s@#]+", '', txt)
      ).map(
         # pprint() can only handle ascii, it seems
         lambda txt: txt.encode('ascii','ignore')
      )

   tweets = KafkaUtils.createDirectStream(ssc, [ 'tweets' ], { "metadata.broker.list": args.bk_endpt })
   harassing_tweets = KafkaUtils.createDirectStream(ssc, [ 'harassing-tweets' ], { "metadata.broker.list": args.bk_endpt })

   c = Singleton.get('tweetClassifier', lambda: RandomTweetClassifier(p=0.01))

   tweets.count().pprint()
   preprocess(tweets).filter(
      lambda txt: c.isHarassingTweet(txt)
   ).pprint()

   harassing_tweets.count().pprint()
   #preprocess(harassing_tweets).flatMap(
      #lambda txt: c.addHarassingTweet(txt)
   #).pprint()

   ssc.start()
   ssc.awaitTermination()
# vim: expandtab shiftwidth=3 softtabstop=3 tabstop=3
