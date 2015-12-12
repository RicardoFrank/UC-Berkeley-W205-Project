from __future__ import print_function
import sys, os
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

sys.path += [ os.getcwd() ]
from classifier.rand import RandomTweetClassifier
from classifier.key_word import KeywordTweetClassifier

c = RandomTweetClassifier(p = 0.01)
server = SimpleXMLRPCServer(("localhost", 6666), allow_none=True)
print("Listening on port 6666...")
server.register_function(lambda txt: (print('checking: ' + txt), c.isHarassingTweet(txt))[1], "isHarassingTweet")
server.register_function(lambda txt: (print('  adding: ' + txt), c.addHarassingTweet(txt))[1], "addHarassingTweet")
server.serve_forever()
