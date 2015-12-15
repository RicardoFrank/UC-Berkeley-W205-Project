import logging
from simserver import SessionServer
import gensim.utils

from classifier.base import TweetClassifier

#logging.basicConfig(filename='/tmp/example.log',level=logging.DEBUG)

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
	self.first = []
	self.initial_corpus_len = 10
        pass

    def _doc(self, txt):
	'''
	Turn processed tweet text into a document used by the model
	'''
	self.docid += 1
	return {
	    'id': 'doc #%d' % self.docid
	    #, 'tokens': list(gensim.utils.tokenize(txt))
	    , 'tokens': gensim.utils.simple_preprocess(txt)
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

	if len(self.first) < self.initial_corpus_len - 1:
	    self.first.append(txt)
	    return

	d = self._doc(txt)
	if self.model is not None:
	    self.model.index([d])
	else:
	    self.model = SessionServer('/tmp/lsi-tweet-classifier')
	    corpus = [self._doc(_) for _ in self.first] + [d]
	    print("initial corpus: ", corpus)
	    self.model.train(corpus, method='lsi')
	    self.model.index(corpus)
 
    def loadModel(self):
        pass

    def saveModel(self, path):
        pass
