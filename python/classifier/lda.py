import random
import logging, gensim, bz2
logging.basicConfig(filename='~/W205-Project/example.log',level=logging.DEBUG)
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
	texts = txt.lower().split()
	corpus_bow = self.d.doc2bow(texts)	# bag of words corpus
	doc_lda = self.model[corpus_bow]
        print(doc_lda)
	harassing = any(_[1] > self.tolerance for _ in doc_lda)
        if harassing:
            print ("    HARASSING tweet '" + txt + "'")
        return harassing

    def addHarassingTweet(self, txt):
	words = txt.lower().split()

	if self.d is None:
	    # build dictionary
	    self.d = gensim.corpora.dictionary.Dictionary([words])

	# generate bag of words
	corpus_bow = self.d.doc2bow(words, allow_update=True)

#	if (self.model is not None) and (corpus_bow is not None):
#	    self.model.update([corpus_bow],update_every=1)
#	else:
	    # build model using this first tweet
	if self.model is None:
	     self.model = LdaModel(corpus=[corpus_bow],num_topics=10, eval_every=10,update_every=1,passes=10)

    def loadModel(self):
        pass

    def saveModel(self, path):
        pass
