from . import BaseModel
class Spacy(BaseModel):  
  def encode(self, text):   
    return text.vector