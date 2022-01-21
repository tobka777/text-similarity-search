import gensim
import gensim.downloader
import numpy as np
from .BaseModel import BaseModel
import spacy

class Gensim(BaseModel):
  remove_stopwords = True

  def encode_word(self, word):
    word = str(word).lower()
    if word in self.model:
      return self.model[word]
    else:
      return np.zeros(300)

  def encode(self, text):
    tokens = [self.encode_word(token) for token in self.preprocess(text, self.remove_stopwords)]
    if len(tokens) == 0:
      return np.zeros(300)
    embedding = np.average(tokens, axis=0, weights=None).reshape(1, -1)
    return embedding

  def download(self, path, name):
    self.load_spacy()
    model = gensim.downloader.load(name)
    model.save(path+name)
    return model

  def load(self, path, name):
    self.load_spacy()
    return gensim.models.KeyedVectors.load(path+name)

  def load_spacy(self):
    if self.lang == 'de':
      self.spy = spacy.load("de_core_news_lg")
    else:
      self.spy = spacy.load("en_core_web_lg")

  def preprocess(self, text, remove_stopwords=False):
    normalized_text = text.replace("‘", "'").replace("’", "'")
    token = self.spy(normalized_text.lower())
    if remove_stopwords:
      return [t.lower_ for t in token if not t.is_stop and not t.is_punct]
    else:
      return token