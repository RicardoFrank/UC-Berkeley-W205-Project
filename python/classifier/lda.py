import random
import logging, gensim, bz2

from gensim.models.ldamodel import LdaModel
from gensim import corpora
from classifier.base import TweetClassifier
from gensim.corpora import TextCorpus, MmCorpus, Dictionary

class LDATweetClassifier(TweetClassifier):
    nInstances = 0

    def __init__(self, tolerance = 0.4, sc = None):
        print('INITIALIZING ' + type(self).__name__)
	self.nInstances += 1
        self.serno = self.nInstances
	self.d = None
	self.model = None
	self.tolerance = tolerance
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
	words = txt.split()

	if self.d is None:
	    # build dictionary
	    self.d = gensim.corpora.dictionary.Dictionary([words])

	# generate bag of words
	bow = self.d.doc2bow(words, allow_update=True)

	if self.model is not None:
	    self.model.update([bow])
	else:
	    # build model using this first tweet
	    self.model = LdaModel(corpus=[bow])

    def loadModel(self):
        pass

    def saveModel(self, path):
        pass
