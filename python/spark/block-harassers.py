import sys, argparse
import pprint
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils


import argparse, pprint

if __name__ == "__main__":
   p = argparse.ArgumentParser(
      description='Spark job to monitor tweets and classify them as harassers'
      , formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   p.add_argument('--broker', dest='bk_endpt', required=True, metavar='ENDPOINT'
		  , help='broker endpoint for kafka store')
   topicDef = 'tweets'
   p.add_argument('--topic', dest='topic'
		  , help='Kafka topic to which tweets are written (default: {0})'.format(topicDef))
   args = p.parse_args()

   sc = SparkContext("local[2]", "block-harassers")
   ssc = StreamingContext(sc, 10)
   ssc.checkpoint("file:///tmp/checkpointing")

   pp = pprint.PrettyPrinter(indent=4)
   pp.pprint(args.bk_endpt)
   ks = KafkaUtils.createDirectStream(ssc, [ 'tweets', 'harassers' ], { "metadata.broker.list": args.bk_endpt })
   ks.pprint()

   ssc.start()
   ssc.awaitTermination()
