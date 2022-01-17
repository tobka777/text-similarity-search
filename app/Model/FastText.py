import numpy as np
import fasttext
from .BaseModel import BaseModel
import spacy
class FastText(BaseModel):  
  remove_stopwords = True

  def encode_word(self, word):   
    return self.model.get_word_vector(str(word).lower())

  def encode(self, text):
    tokens = [self.encode_word(token) for token in self.preprocess(text, self.remove_stopwords) if np.linalg.norm(self.encode_word(token)) > 0]
    if len(tokens) == 0:
      return np.zeros(300)
    embedding = np.average(tokens, axis=0, weights=None).reshape(1, -1)
    return embedding
  
  def download(self, path, name):
    print("Please download and put the model '"+name+"' in the folder '"+path+name+"'.")
    exit()

  def load(self, path, name):
    if self.lang == 'de':
      self.spy = spacy.load("de_core_news_lg")
    else:
      self.spy = spacy.load("en_core_web_lg")
    return fasttext.load_model(path+name)
  
  def preprocess(self, text, remove_stopwords=False):
    normalized_text = text.replace("‘", "'").replace("’", "'")
    token = self.spy(normalized_text.lower())
    if remove_stopwords:
      return [t.lower_ for t in token if not t.is_stop and not t.is_punct]
    else:
      return token