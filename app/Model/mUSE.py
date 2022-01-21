from .BaseModel import BaseModel
import tensorflow_hub as hub
import tensorflow_text
import os

class mUSE(BaseModel):  
  def encode(self, text):   
    return self.model([text])

  def download(self, path, name):
    os.environ["TFHUB_CACHE_DIR"] = path
    return hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")

  def load(self, path, name):
    return self.download(path, name)
