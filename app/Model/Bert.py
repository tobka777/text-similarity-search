from transformers import BertTokenizer, TFBertModel
from .BaseModel import BaseModel
import spacy
import numpy as np

class Bert(BaseModel):
  remove_stopwords = True

  def encode_word(self, word):  
    encoded_input = self.tokenizer(word, return_tensors='tf')
    return self.model(encoded_input)

  def encode(self, text):
    tokens = [self.encode_word(token) for token in self.preprocess(text, self.remove_stopwords)]
    if len(tokens) == 0:
      return np.zeros(300)
    embedding = np.average(tokens, axis=0, weights=None).reshape(1, -1)
    return embedding

  def download(self, path, name):
    tokenizer = BertTokenizer.from_pretrained(name, cache_dir=path)
    model = TFBertModel.from_pretrained(name)
    self.tokenizer = tokenizer
    return model

  def load(self, path, name):
    if self.lang == 'de':
      self.spy = spacy.load("de_core_news_lg")
    else:
      self.spy = spacy.load("en_core_web_lg")
    return self.download(path, name)
  
  def preprocess(self, text, remove_stopwords=False):
    normalized_text = text.replace("‘", "'").replace("’", "'")
    token = self.spy(normalized_text.lower())
    if remove_stopwords:
      return [t.lower_ for t in token if not t.is_stop and not t.is_punct]
    else:
      return token