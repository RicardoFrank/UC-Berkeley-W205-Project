import logging
from simserver import SessionServer

from classifier.base import TweetClassifier

logging.basicConfig(filename='/tmp/example.log',level=logging.DEBUG)

class LSITweetClassifier(TweetClassifier):
    nInstances = 0
    
    def __init__(self, tolerance = 0.4, sc = None):
        print('INITIALIZING ' + type(self).__name__)
	self.nInstances += 1
        self.serno = self.nInstances
	self.docid = 0
	self.harassment = {}
	self.model = None
	self.tolerance = tolerance
        pass

    def _doc(self, txt):
	'''
	Turn processed tweet text into a document used by the model
	'''
	return {
	    'id': 'doc #%d' % str(self.docid++)
	    , 'tokens': txt.split()
	}

    def isHarassingTweet(self, txt):
	if self.model is None:
	    # Nothing to see here
	    return False

	sims = self.model.find_similar(self._doc(txt), min_score=self.tolerance, max_results=1)
	harassing = len(sims) > 0
        if harassing:
            print ("    HARASSING tweet '" + txt + "'")
        return harassing

    def addHarassingTweet(self, txt):
	'''
	Add an harassing tweet to the model corpus
	'''

	if txt in self.harassment: return
	self.harassment[txt] = 1

	d = self._doc(txt)
	if self.model is not None:
	    self.model.index(d)
	else:
	    self.model = SessionServer('/tmp/lsi-tweet-classifier')
	    self.model.train(d, method='lsi')
 
    def loadModel(self):
        pass

    def saveModel(self, path):
        pass
