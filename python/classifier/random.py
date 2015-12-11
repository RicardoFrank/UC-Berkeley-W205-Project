import random
import classifier.TweetClassifier

class RandomTweetClassifier(TweetClassifier):
    harassing_p = 0.5

    def __init__(self, sc, p = 0.5):
	TweetClassifier.__init__(self, sc)
	self.harassing_p = p

    def isHarrassingTweet(self, txt):
    	return random.random() < self.harassing_p

    def addHarrassingTweet(self, txt):
	pass
