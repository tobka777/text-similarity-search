from abc import ABC, abstractmethod
import os
class BaseModel(ABC):
  def __init__(self, name, lang='de'):
    self.lang = lang
    path = "data/"
    filepath = os.path.expanduser(path+name)
    if os.path.isfile(filepath):
      model = self.load(path, name)
    else:
      model = self.download(path, name)
    self.model = model

  @abstractmethod
  def encode(self, text: str):
    """Load vector from model."""
    pass

  @abstractmethod
  def download(self, path, name):
    """Download model."""
    pass

  @abstractmethod
  def load(self, path, name):
    """Load model."""
    pass
