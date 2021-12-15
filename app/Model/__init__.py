from abc import ABC, abstractmethod
import numpy as np
import os

class BaseModel(ABC):
  def __init__(self, name):
    path = os.path.expanduser("data/"+name+".model")
    if os.path.isfile(path):
      model = self.load(path)
    else:
      model = self.download(name)
      self.save(model, path)
    self.model = model

  @abstractmethod
  def encode(self, text: str):
    """Load vector from model."""
    pass

  @abstractmethod
  def download(self, name):
    """Download model."""
    pass

  @abstractmethod
  def load(self, path):
    """Load model."""
    pass

  @abstractmethod
  def save(self, model, path):
    """Save model."""
    pass
