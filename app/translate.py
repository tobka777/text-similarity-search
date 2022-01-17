import sys
import os
from Benchmark import SICK

benchmark = SICK()

data = benchmark.load_dataset_from_file("data/sickbenchmark/en/sick-dev.csv", 1, 2, 3, ",", True)
#data = benchmark.load_dataset_from_file("data/sickbenchmark/de/sick-dev.csv", 1, 2, 3, ",", True)

for i, row in data.iterrows():
  t1 = benchmark.translate(row[1],'DE')
  t2 = benchmark.translate(row[2],'DE')
  data.at[i,1] = t1
  data.at[i,2] = t2

data.to_csv("Benchmark/data/sickbenchmark/de/dev.csv", sep=";", encoding='utf-8', index=False, header=False)

