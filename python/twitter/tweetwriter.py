from __future__ import print_function
import tweepy
import traceback
from util.reentrantmethod import ReentrantMethod

class TweetWriter(tweepy.StreamListener):
   '''
   Write a stream of tweets using a serializer
   '''
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
