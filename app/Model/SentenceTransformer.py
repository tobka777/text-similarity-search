class SentenceTransformer(BaseModel):  
  def vector(self, text):   
    return self.model.encode(text)