class TweetClassifier(object):
    model = None

    def __init__(self, sc=None):
	if sc is None:
	    raise ValueError('no spark context provided)
	self.sc = sc

    def isHarrassingTweet(self, txt):
    	pass

    def addHarrassingTweet(self, txt):
	pass

    def loadModel(self, path):
	model = self.sc.textFile(path)

    def saveModel(self, path):
	model = self.sc.saveAsTextFile(path)
