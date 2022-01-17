from .BaseModel import BaseModel
import tensorflow_hub as hub

class mUSE(BaseModel):  
  def encode(self, text):   
    return self.model([text])

  def download(self, path, name):
    return hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")

  def load(self, path, name):
    return self.download(path, name)
