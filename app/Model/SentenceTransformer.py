from .BaseModel import BaseModel
from sentence_transformers import SentenceTransformer as SentTrans
class SentenceTransformer(BaseModel):  
  def encode(self, text):   
    return self.model.encode(text)

  def download(self, path, name):
    return SentTrans(name, cache_folder=path)

  def load(self, path, name):
    return SentTrans(path+name)