import sys, os
import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer


sys.path += [ os.getcwd() ]
from classifier.rand import RandomTweetClassifier
from classifier.keyword import KeywordTweetClassifier
#sys.path += [ os.getcwd() + '/classifier' ]
#for p in sys.path: print(p)
#import rand
#from rand import RandomTweetClassifier
#from classifier.keyword import KeywordTweetClassifier

c = RandomTweetClassifier(p = 0.01)
def isHarassingTweet(txt):
    return c.isHarassingTweet(txt)

def addHarassingTweet(txt):
    c.addHarassingText(txt)

server = SimpleXMLRPCServer(("localhost", 6666))
print "Listening on port 6666..."
server.register_function(isHarassingTweet, "isHarassingTweet")
server.register_function(addHarassingTweet, "addHarassingTweet")
server.serve_forever()
