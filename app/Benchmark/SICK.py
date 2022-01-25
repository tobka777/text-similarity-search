import pandas as pd
from .BaseBenchmark import BaseBenchmark
import os

class SICK(BaseBenchmark):
  def load_dataset(self, lang='en'):
    if lang=='de':
      train = self.load_dataset_from_file("data/sickbenchmark/de/sick-train.csv", 1, 2, 3, ";")
      dev = self.load_dataset_from_file("data/sickbenchmark/de/sick-dev.csv", 1, 2, 3, ";")
      test = self.load_dataset_from_file("data/sickbenchmark/de/sick-test.csv", 1, 2, 3, ";")
      return pd.concat([train, dev, test])
    else:
      train = self.load_dataset_from_file("data/sickbenchmark/en/sick-train.csv", 1, 2, 3, ",")
      dev = self.load_dataset_from_file("data/sickbenchmark/en/sick-dev.csv", 1, 2, 3, ",")
      test = self.load_dataset_from_file("data/sickbenchmark/en/sick-test.csv", 1, 2, 3, ",")
    return pd.concat([train, dev, test])