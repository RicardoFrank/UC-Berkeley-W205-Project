import json
from util.reentrantmethod import ReentrantMethod

class TweetSerializer(object):

   def __init__(self, store = None, to_json = staticmethod(lambda j: j)):
      self.store = store
      self.ended = True
      self.first = None
      self._to_json_obj = to_json
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
      self.store.writeTweet(json.dumps(self._to_json_obj(tweet)
                                       , indent=4
                                       , separators=(',', ': ')).encode('utf8'))

   def closing(self):
      self.end()
