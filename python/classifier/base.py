class TweetClassifier(object):
    model = None

    def __init__(self, sc=None):
	if sc is None:
	    #raise ValueError('no spark context provided')
	    pass
	self.sc = sc

    def isHarassingTweet(self, txt):
    	pass

    def addHarassingTweet(self, txt):
	pass

    def loadModel(self, path):
	pass

    def saveModel(self, path):
	pass
