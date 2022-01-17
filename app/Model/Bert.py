from transformers import BertTokenizer, TFBertModel
from .BaseModel import BaseModel

class Bert(BaseModel):
  def encode(self, text):  
    encoded_input = self.tokenizer(text, return_tensors='tf')
    return self.model(encoded_input)

  def download(self, path, name):
    tokenizer = BertTokenizer.from_pretrained(name, cache_dir=path)
    model = TFBertModel.from_pretrained(name)
    self.tokenizer = tokenizer
    return model

  def load(self, path, name):
    return self.download(path, name)