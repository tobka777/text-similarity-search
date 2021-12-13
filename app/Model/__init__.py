from abc import ABC, abstractmethod
import numpy as np

class BaseModel(ABC):
  def __init__(self, model):
    self.model = model

  @abstractmethod
  def vector(self, text: str) -> list:
    """Load vector from model."""
    pass
