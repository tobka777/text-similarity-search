from . import BaseModel
class SentenceTransformer(BaseModel):  
  def encode(self, text):   
    return self.model.encode(text)