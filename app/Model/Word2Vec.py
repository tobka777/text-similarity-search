class Word2Vec(BaseModel):  
  def vector(self, text):   
    if str(text).lower() in self.model:  
      return self.model[str(text).lower()]
    else:
      return np.zeros(300)