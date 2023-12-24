import sys
import os
from SICK import SICK

benchmark = SICK()

data = benchmark.load_dataset_from_file("data/sickbenchmark/en/sick-train.csv", 1, 2, 3, ",", True)

for i, row in data.iterrows():
  t1 = benchmark.translate(row[1],'DE')
  t2 = benchmark.translate(row[2],'DE')
  data.at[i,1] = t1
  data.at[i,2] = t2
  with open("data/sickbenchmark/de/sick-train_bak.csv", "a") as f:
    f.write(data.iloc[[i]].to_csv(sep=";", encoding='utf-8', index=False, header=False))

data.to_csv("data/sickbenchmark/de/sick-train.csv", sep=";", encoding='utf-8', index=False, header=False)