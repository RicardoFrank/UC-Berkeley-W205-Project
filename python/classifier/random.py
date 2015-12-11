import random
import classifier.TweetClassifier

class RandomTweetClassifier(TweetClassifier):
    harassing_p = 0.5

    def __init__(self, p = 0.5, sc):
	TweetClassifier.__init__(self, sc)
	self.harassing_p = p

    def isHarrassingTweet(self, txt):
    	return random.random() < self.harassing_p

    def addHarrassingTweet(self, txt):
	pass
