class FastText(BaseModel):  
  def vector(self, text):   
    return self.model.get_word_vector(str(text).lower())