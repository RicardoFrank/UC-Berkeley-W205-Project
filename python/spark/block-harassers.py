import sys, argparse
import json, re
import pprint
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

sys.path += [ '.' ]
#from spark.lda import Classifier
#from tweets.text

if __name__ == "__main__":
   p = argparse.ArgumentParser(
      description='Spark job to monitor tweets and classify them as harassers'
      , formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   p.add_argument('--broker', dest='bk_endpt', required=True, metavar='ENDPOINT'
		  , help='broker endpoint for kafka store')
   args = p.parse_args()

   sc = SparkContext("local[2]", "block-harassers")
   ssc = StreamingContext(sc, 10)
   ssc.checkpoint("file:///tmp/checkpointing")

   pp = pprint.PrettyPrinter(indent=4)
   pp.pprint(args.bk_endpt)

   tweets = KafkaUtils.createDirectStream(ssc, [ 'tweets' ], { "metadata.broker.list": args.bk_endpt })
   harassing_tweets = KafkaUtils.createDirectStream(ssc, [ 'harassing-tweets' ], { "metadata.broker.list": args.bk_endpt })

   tweets.count().pprint()

   harassing_tweets.count().pprint()
   harassing_tweets.map(
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
   ).pprint()

   ssc.start()
   ssc.awaitTermination()
# vim: expandtab shiftwidth=3 softtabstop=3 tabstop=3
