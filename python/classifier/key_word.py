import random

from classifier.base import TweetClassifier

class KeywordTweetClassifier(TweetClassifier):
    nInstances = 0

    def __init__(self, sc = None):
	print('INITIALIZING ' + type(self).__name__)
	self.model = {}
	self.nInstances += 1
	self.serno = self.nInstances
	pass

    def isHarassingTweet(self, txt):
    	for s in txt.split():
	    if s in self.model:
		print("    HARASSING keyword '" + s + "' in '" + txt + "'")
		return True
	print("not harassing: '" + txt + "'")
	return False

    def addHarassingTweet(self, txt):
	for s in txt.split():
	    if not s in self.model:
		print("%d adding '%s' to model" % (self.serno, s))
	    self.model[s] = 1

    def loadModel(self):
	pass

    def saveModel(self, path):
	pass
