import spacy as spy
import numpy as np
from .BaseModel import BaseModel
from sklearn.decomposition import TruncatedSVD

class SIF(BaseModel):  
  def encode_word(self, word):   
    return word.vector

  def encode(self, text):
    tokens = [self.encode_word(token) for token in self.model(text)]
    if len(tokens) == 0:
      return np.zeros(300)
    embedding = np.average(tokens, axis=0, weights=None)
    embedding = self.remove_first_principal_component(np.array([embedding]), npc=1).reshape(1, -1)
    return embedding

  def download(self, path, name):
    return spy.load(name)

  def load(self, path, name):
    return self.download(path, name)

  def remove_first_principal_component(self, X, npc=1):
    svd = TruncatedSVD(n_components=npc, n_iter=7, random_state=0)
    svd.fit(X)
    pc = svd.components_
    if npc==1:
        XX = X - X.dot(pc.transpose()) * pc
    else:
        XX = X - X.dot(pc.transpose()).dot(pc)
    return XX