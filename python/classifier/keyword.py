import random

from classifier.base import TweetClassifier

class KeywordTweetClassifier(TweetClassifier):
    model = {}

    def __init__(self, sc = None, p = 0.5):
	TweetClassifier.__init__(self, sc)

    def isHarassingTweet(self, txt):
    	for s in txt.split():
	    if s in self.model:
		return True
	return False

    def addHarassingTweet(self, txt):
	for s in txt.split():
	    self.model[s] = 1

    def loadModel(self, textRDD = None):
	pass
	#self.model = {}
	#for s in textRDD:
	    #self.model[s] = 1

    def saveModel(self, path):
	pass

