from .BaseModel import BaseModel
class FastText(BaseModel):  
  def encode(self, text):   
    return self.model.get_word_vector(str(text).lower())