import spacy as spy
import numpy as np
from .BaseModel import BaseModel
class Spacy(BaseModel):  
  def encode_word(self, word):   
    return word.vector

  def encode(self, text):
    tokens = [self.encode_word(token) for token in self.model(text)]
    if len(tokens) == 0:
      return np.zeros(300)
    embedding = np.average(tokens, axis=0, weights=None).reshape(1, -1)
    return embedding

  def download(self, path, name):
    return spy.load(name)

  def load(self, path, name):
    return self.download(path, name)