import xmlrpclib

from classifier.base import TweetClassifier

class RemoteTweetClassifier(TweetClassifier):
    """
    Create a proxy to a remote TweetClassifier
    """
    def __init__(self, endpt):
	self.proxy = None	# Set to None so closures over an instance will know to create the proxy
	self.endpt = endpt

    def isHarassingTweet(self, txt):
	print("checking: " + txt)
	if self.proxy is None:
	    self.proxy = xmlrpclib.ServerProxy(self.endpt, allow_none = True)
        return self.proxy.isHarassingTweet(txt)

    def addHarassingTweet(self, txt):
	print("  adding: " + txt)
	if self.proxy is None:
	    self.proxy = xmlrpclib.ServerProxy(self.endpt, allow_none = True)
        self.proxy.addHarassingTweet(txt)


