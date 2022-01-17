from .BaseModel import BaseModel
import torch

class XLR(BaseModel):
  def encode(self, text):   
    self.model.encode(text)

  def download(self, path, name):
    torch.hub.set_dir(path)
    print(torch.hub.get_dir())
    return torch.hub.load('pytorch/fairseq', 'xlmr.large')

  def load(self, path, name):
    return self.download(path, name)
