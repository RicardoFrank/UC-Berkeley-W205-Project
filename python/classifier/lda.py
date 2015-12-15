import random
import os
import logging, gensim, bz2
logging.basicConfig(filename='example.log',level=logging.DEBUG)
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
	self.id2word = None
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

	#if self.d is None:
	    # build dictionary
	self.d = gensim.corpora.dictionary.Dictionary([words])
	self.d.save('/tmp/singletweet')
	# generate bag of words
	corpus_bow = self.d.doc2bow(words, allow_update=True)
	if self.id2word is None:
	   self.id2word = gensim.corpora.Dictionary.load('/tmp/singletweet')
	if (self.model is not None) and (corpus_bow is not None):
	    self.model.update([corpus_bow],update_every=1)
	else:
	    # build model using this first tweet
	    self.model = LdaModel(corpus=None,num_topics=10,id2word=self.id2word, eval_every=10,update_every=1,passes=10)
	os.remove('/tmp/singletweet')
 
    def loadModel(self):
        pass

    def saveModel(self, path):
        pass
