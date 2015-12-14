import random
import logging, gensim, bz2

from stop_words import get_stop_words
from gensim.models.ldamodel import LdaModel
from gensim import corpora
from classifier.base import TweetClassifier
from gensim.corpora import TextCorpus, MmCorpus, Dictionary

class LDATweetClassifier(TweetClassifier):
    nInstances = 0

    def __init__(self, sc = None):
        print('INITIALIZING ' + type(self).__name__)
	self.nInstances += 1
        self.serno = self.nInstances
        pass

    def isHarassingTweet(self, txt):
	if mycorpus is None:
	  d = gensim.corpora.dictionary.Dictionary(['this is an harassing tweet, dammit'.lower().split()])
	  mycorpus = [d.doc2bow('this is an harassing tweet'.lower())]
	  mycorpus = dictionary.doc2bow(txt.lower().split(),allow_update=True)
        print("isHarassing begin")	
	mycorpus = mycorpus.add_documents(txt.lower(),prune_at=2000000) 
	
	if lda is None:
	  lda = LdaModel(corpus=mycorpus, num_topics=100, id2word=None, distributed=False, chunksize=2000, passes=1, update_every=1, alpha='symmetric', eta=None, decay=0.5, offset=1.0, eval_every=10, iterations=50, gamma_threshold=0.001, minimum_probability=0.01)
        
	doc_lda = lda[txt.lower()]
        print(doc_lda)
        if doc_lda > 0.15:
          print ("    HARASSING tweet '" + txt + "'")
          return True

        return False


    def addHarassingTweet(self, txt):
        self.model.update(txt.lower())

    def loadModel(self):
        pass


    def saveModel(self, path):
        pass
