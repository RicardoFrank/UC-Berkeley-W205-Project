import sys, argparse
import argparse, pprint, json
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
      lambda s: json.loads(s[1])['text']	# pluck out tweet's text
   ).map(
      lambda t: t.encode('ascii','ignore')	# pprint() can only handle ascii, it seems
   ).pprint()

   ssc.start()
   ssc.awaitTermination()
