from __future__ import print_function
import sys, os
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

sys.path += [ os.getcwd() ]
from classifier.rand import RandomTweetClassifier
from classifier.key_word import KeywordTweetClassifier
from classifier.lda import LDATweetClassifier
from classifier.lsi import LSITweetClassifier

from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

class handler(SimpleXMLRPCRequestHandler):
     def _dispatch(self, method, params):
         try: 
             return self.server.funcs[method](*params)
         except:
             import traceback
             traceback.print_exc()
             raise

#c = RandomTweetClassifier(p = 0.01)
#c = KeywordTweetClassifier()
#c = LDATweetClassifier()
c = LSITweetClassifier()
server = SimpleXMLRPCServer(('', 6666), handler, allow_none=True)
print("Listening on port 6666...")
server.register_function(lambda txt: (print('checking: ' + txt), c.isHarassingTweet(txt))[1], "isHarassingTweet")
server.register_function(lambda txt: (print('  adding: ' + txt), c.addHarassingTweet(txt))[1], "addHarassingTweet")
server.serve_forever()
