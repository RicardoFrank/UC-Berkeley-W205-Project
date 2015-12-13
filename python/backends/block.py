from __future__ import print_function
import sys, os, signal
import tweepy, json
import argparse, pprint

sys.path += [ os.getcwd() ]
from util.kafkatransceiver import KafkaTransceiver

if __name__ == '__main__':

   p = argparse.ArgumentParser(
      description='Listen for harassers and add them to a block list'
      , formatter_class=argparse.ArgumentDefaultsHelpFormatter)
   p.add_argument('--broker', dest='bk_endpt', metavar='ENDPOINT', default='localhost:9092'
                  , help='kafka broker endpoint')
   p.add_argument('--topic', dest='topic', default='harassers'
                  , help='Kafka topic from which tweets are read')

   args = p.parse_args()
   pp = pprint.PrettyPrinter(indent=4)
   pp.pprint(args)

   execfile('./creds.py')
   auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
   auth.set_access_token(access_token, access_token_secret)
   api = tweepy.API(auth_handler=auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
   me = api.me().screen_name

   k = KafkaTransceiver(args.bk_endpt)

   def quit(signum, frame):
      k.close()
      exit()
   signal.signal(signal.SIGINT, quit)
   signal.signal(signal.SIGTERM, quit)

   while True:
      m = k.recv(args.topic)
      m = json.loads(m)
      try:
         api.create_block(m['author'])
         print('@%s has blocked @%s for tweeting "%s"' % (me, m['author'], m['text']))
      except:
         print("Error blocking @%s: %s" % (m['author'], sys.exc_info()[0]))
   quit()


# vim: expandtab shiftwidth=3 softtabstop=3 tabstop=3
