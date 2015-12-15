import logging
from gensim.models.ldamodel import LdaModel
from gensim.corpora import Dictionary

from classifier.base import TweetClassifier

logging.basicConfig(filename='/tmp/example.log',level=logging.DEBUG)

class LDATweetClassifier(TweetClassifier):
    nInstances = 0
    
    def __init__(self, tolerance = 0.4, sc = None):
        print('INITIALIZING ' + type(self).__name__)
	self.nInstances += 1
        self.serno = self.nInstances
	self.d = None
	self.model = None
	self.tolerance = tolerance
	self.harassment = {}
        pass

    def isHarassingTweet(self, txt):
	if self.model is None:
	    # Nothing to see here
	    return False

	bow = self.d.doc2bow(txt.split())	# bag of words
	doc_lda = self.model[bow]
        print(doc_lda)
	harassing = any(_[1] > self.tolerance for _ in doc_lda)
        if harassing:
            print ("    HARASSING tweet '" + txt + "'")
        return harassing

    def addHarassingTweet(self, txt):
	'''
	Add an harassing tweet to the model corpus

	While gensim purports to train models incrementally,
	it'll crash if you try.  Instead, we just rebuild
	the model each time we get a new tweet, remembering
	all the old ones as we go.
	'''
	if txt in self.harassment:
	    return

	words = txt.split()

	if self.d is None:
	    # build dictionary
	    self.d = Dictionary([words])

	# generate bag of words
	bow = self.d.doc2bow(words, allow_update=True)
	self.harassment[txt] = bow

	corpus = []
	for txt in self.harassment:
	    corpus.append(self.harassment[txt])

	self.model = LdaModel(corpus)
 
    def loadModel(self):
        pass

    def saveModel(self, path):
        pass
