import gensim
import gensim.downloader
import os
from . import BaseModel

class Word2Vec(BaseModel):
  def encode(self, text):   
    if str(text).lower() in self.model:  
      return self.model[str(text).lower()]
    else:
      return np.zeros(300)

  def download(self, name):
    return gensim.downloader.load(name)

  def load(self, path):
    return gensim.models.KeyedVectors.load(path)
    return gensim.models.Word2Vec.load(path)
    #return gensim.models.KeyedVectors.load_word2vec_format(path, binary=False)

  def save(self, model, path):
    model.save(path)