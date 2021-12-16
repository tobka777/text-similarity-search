import gensim
import gensim.downloader
import numpy as np
from .BaseModel import BaseModel

class Word2Vec(BaseModel):
  def encode(self, text):   
    if str(text).lower() in self.model:  
      return self.model[str(text).lower()]
    else:
      return np.zeros(300)

  def download(self, path, name):
    model = gensim.downloader.load(name)
    model.save(path+name)
    return model

  def load(self, path, name):
    return gensim.models.KeyedVectors.load(path+name)