import pandas as pd

class STSB(BaseBenchmark):
  def load_dataset(self, lang='en'):
    if lang=='de':
      train = self.load_dataset_from_file("data/stsbenchmark/de/sts-train.csv", 1, 2, 0, "\t")
      dev = self.load_dataset_from_file("data/stsbenchmark/de/sts-dev.csv", 1, 2, 0, "\t")
      test = self.load_dataset_from_file("data/stsbenchmark/de/sts-test.csv", 1, 2, 0, "\t")
    else:
      train = self.load_dataset_from_file("data/stsbenchmark/en/sts-train.csv", 5, 6, 4, "\t")
      dev = self.load_dataset_from_file("data/stsbenchmark/en/sts-dev.csv", 5, 6, 4, "\t")
      test = self.load_dataset_from_file("data/stsbenchmark/en/sts-test.csv", 5, 6, 4, "\t")
    return pd.concat([train, dev, test])