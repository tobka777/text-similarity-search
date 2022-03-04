import csv
import pandas as pd
import requests
import math
import numpy as np
import time

name = "sgic"
filename = name+"_test_quality.csv"
dataset = []
with open('data/'+filename, 'r', encoding='utf-8') as f:
  reader = csv.reader(f, delimiter=';', quotechar='"')
  for ts in reader:
    dataset.append(ts)

def calc_evaluation_metrics(row, req, doclen, resultdocs):
  tp = 0
  tn = 0
  fp = 0
  fn = 0
  relevantdoc = 0
  for j in range(5):
    if row["res"+str(j+1)]:
      found = False
      relevantdoc += 1
      for i in range(resultdocs):
        if row["res"+str(j+1)] == req["matches"][i]["id"]:
          found = True
      if found:
        tp += 1
  fp = resultdocs - tp
  fn = relevantdoc - tp
  tn = doclen - resultdocs - fn
  precision = tp / (tp+fp) if tp>0 or fp>0 else 0
  recall = tp / (tp+fn) if tp>0 or fn>0 else 0
  acc = (tp+tn)/(tp+tn+fp+fn)
  f1 = 2*precision*recall / (precision+recall) if precision>0 or recall>0 else 0
  mcc = (tp*tn - fp*fn) / math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)) if ((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)) > 0 else 0
  return [row["query"], tp, fp, fn, tn, round(precision,1), round(recall,2), round(acc,2), round(f1,2), round(mcc,2)]

df = pd.DataFrame(dataset, columns=["attribute","query","res1","res2","res3","res4","res5"])
matrix = []
matrix_time = []
doclen = 73
resultdocs = 5
rs = []
all_timer_start = time.time()
for index, row in df.iterrows():
  if row["query"] and hasattr(row, "res1"):
    timer_start = time.time()
    r=requests.get('https://search.seriousgames-portal.org/api/search?query='+row["query"])
    timer = time.time() - timer_start
    req=r.json()
    matrix_time.append([row["query"],req["time"]["embed"],req["time"]["elastic"],float(r.headers["x-process-time"]),timer])

    eval_res = calc_evaluation_metrics(row, req, doclen, resultdocs)

    ##### MAP #######
    ap = 0
    for i in range(1,resultdocs):
      ap += calc_evaluation_metrics(row, req, doclen, i)[5]
    ap = 1/(resultdocs-1) * ap
    eval_res.append(ap)

    ##### Precision at rank p #######
    precision_rank_10 = calc_evaluation_metrics(row, req, doclen, 10)[5] #p=10
    eval_res.append(precision_rank_10)
 
    matrix.append(eval_res)
  #time.sleep(2)

all_timer = time.time() - all_timer_start
print(all_timer)

eval_matrix = pd.DataFrame(matrix, columns=["query","tp","fp","fn","tn","precision","recall","acc","f1","mcc","map","precision_rank_10"])

result_folder = 'result/'+name+'_'
eval_matrix.to_csv(result_folder+'result_eval_matrix.csv')  
eval_matrix.describe().to_csv(result_folder+'result_eval_matrix_stat.csv')  

eval_matrix_time = pd.DataFrame(matrix_time, columns=["query","embed","elastic","process","process + network"])
eval_matrix_time.to_csv(result_folder+'result_eval_matrix_time.csv')  
eval_matrix_time.describe().to_csv(result_folder+'result_eval_matrix_time_stat.csv')  