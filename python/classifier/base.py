class TweetClassifier(object):
    model = None

    def __init__(self, sc=None):
	if sc is None:
	    raise ValueError('no spark context provided')
	self.sc = sc

    def isHarassingTweet(self, txt):
    	pass

    def addHarassingTweet(self, txt):
	pass

    def loadModel(self, path):
	model = self.sc.textFile(path)

    def saveModel(self, path):
	model = self.sc.saveAsTextFile(path)
