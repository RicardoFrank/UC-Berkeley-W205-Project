import random


from gensim.models.ldamodel import LdaModel
from classifier.base import TweetClassifier

class LDATweetClassifier(TweetClassifier):
    nInstances = 0

    def __init__(self, sc = None):
        print('INITIALIZING ' + type(self).__name__)
        self.model = LdaModel(corpus=None, num_topics=100, id2word=None, distributed=False, chunksize=2000, passes=1, update_every=1, alpha='symmetric', eta=None, decay=0.5, offset=1.0, eval_every=10, iterations=50, gamma_threshold=0.001, minimum_probability=0.01
        self.nInstances += 1
        self.serno = self.nInstances
        pass

    def isHarassingTweet(self, txt):
        doc_lda = self.model[txt]
        print(doc_lda)
        if doc_lda > 0.15
          print ("    HARASSING tweet '" + txt + "'")
          return True

        return False


    def addHarassingTweet(self, txt):
        self.model.update(txt)

    def loadModel(self):
        pass


    def saveModel(self, path):
        pass
