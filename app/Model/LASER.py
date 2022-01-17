import numpy as np
import os
from .BaseModel import BaseModel
from laserembeddings import Laser

class LASER(BaseModel):  
  def encode(self, text):   
    return self.model.embed_sentences([text], lang=self.lang)

  def download(self, path, name):
    os.system("laserembeddings download-models "+path)
    exit()
    return self.load(path, name)

  def load(self, path, name):
    path_to_bpe_codes = ...
    path_to_bpe_vocab = ...
    path_to_encoder = ...
    return Laser()