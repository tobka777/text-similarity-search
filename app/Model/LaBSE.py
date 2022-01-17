from .BaseModel import BaseModel
import numpy as np
import tensorflow_hub as hub

class LaBSE(BaseModel):  
  def encode(self, text):   
    return self.normalization(self.model(self.preprocessor([text]))["default"])

  def download(self, path, name):
    preprocessor = hub.KerasLayer("https://tfhub.dev/google/universal-sentence-encoder-cmlm/multilingual-preprocess/2")
    encoder = hub.KerasLayer("https://tfhub.dev/google/LaBSE/2")  
    self.preprocessor = preprocessor
    return encoder

  def load(self, path, name):
    return self.download(path, name)

  def normalization(embeds):
    norms = np.linalg.norm(embeds, 2, axis=1, keepdims=True)
    return embeds/norms