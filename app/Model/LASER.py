import numpy as np
import os
from .BaseModel import BaseModel
from laserembeddings import Laser

class LASER(BaseModel):  
  def encode(self, text):   
    return self.model.embed_sentences([text], lang=self.lang)

  def download(self, path, name):
    os.system("python -m laserembeddings download-models "+path)
    return self.load(path, name)

  def load(self, path, name):
    path_to_bpe_codes = path+"93langs.fcodes"
    path_to_bpe_vocab = path+"93langs.fvocab"
    path_to_encoder = path+"bilstm.93langs.2018-12-26.pt"
    return Laser(path_to_bpe_codes, path_to_bpe_vocab, path_to_encoder)