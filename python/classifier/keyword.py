import random

from classifier.base import TweetClassifier

class KeywordTweetClassifier(TweetClassifier):
    nInstances = 0

    def __init__(self, sc = None):
	#TweetClassifier.__init__(self, sc)
	print('INITIALIZING ' + type(self).__name__)
	self.model = {}
	self.nInstances += 1
	self.serno = self.nInstances
	pass

    def isHarassingTweet(self, txt):
	print("%d model is now:\n\t%s"
	      % (self.serno, "\n\t".join(self.model.keys())))
    	for s in txt.split():
	    print("%d checking '%s'" % (self.serno, s))
	    if s in self.model:
		print("    HARASSING keyword '" + s + "' in '" + txt + "'")
		return True
	print("not harassing: '" + txt + "'")
	return False

    def addHarassingTweet(self, txt):
	for s in txt.split():
	    self.model[s] = 1
	print("%d model is now:\n\t %s"
	      % (self.serno, "\n\t".join(self.model.keys())))


    def loadModel(self, textRDD = None):
	pass
	#self.model = {}
	#for s in textRDD:
	    #self.model[s] = 1

    def saveModel(self, path):
	pass
