from abc import ABC, abstractmethod
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import scipy
import requests
import os
import csv
from tqdm import tqdm
import time

DEEPL_API_KEY = os.environ.get('DEEPL_API_KEY', '')

class BaseBenchmark(ABC):
  def load_dataset_from_file(self, filename, sent1, sent2, sim, delimiter="\t", all=False):
    path = os.path.dirname(os.path.realpath(__file__))
    sent_pairs = []
    with open(path+'/'+filename, 'r') as f:
        reader = csv.reader(f, delimiter=delimiter, quotechar='"')
        for ts in reader:
            if all:
              sent_pairs.append(ts)
            else:
              sent_pairs.append((ts[sent1], ts[sent2], float(ts[sim])))
    if all:
      return pd.DataFrame(sent_pairs)
    else:
      return pd.DataFrame(sent_pairs, columns=["sent_1", "sent_2", "sim"])

  @abstractmethod
  def load_dataset(self, lang):
    pass

  def run(self, model, lang='en'): 
    data = self.load_dataset(lang)
    sentences1 = data['sent_1']
    sentences2 = data['sent_2']

    similarities = []
    embed_times = []
    for (sent1, sent2) in tqdm(zip(sentences1, sentences2), total=len(data.index)): 
      time_embed_start = time.time()
      embedding1 = model.encode(sent1).reshape(1, -1)
      time_embed = time.time() - time_embed_start
      embed_times.append(time_embed)

      time_embed_start = time.time()
      embedding2 = model.encode(sent2).reshape(1, -1)
      time_embed = time.time() - time_embed_start
      embed_times.append(time_embed)

      similarity = cosine_similarity(embedding1, embedding2)[0][0]
      similarities.append(similarity)

    pearson_correlation = scipy.stats.pearsonr(similarities, data['sim'])[0]
    spearman_correlation = scipy.stats.spearmanr(similarities, data['sim'])[0]
    embed_time = [sum(embed_times)/len(embed_times), min(embed_times), max(embed_times)]

    return (pearson_correlation, spearman_correlation, embed_time)

  def translate(self, text, target_language):
    result = requests.get( 
      "https://api-free.deepl.com/v2/translate", 
      params={ 
        "auth_key": DEEPL_API_KEY, 
        "target_lang": target_language, 
        "text": text, 
      }, 
    ) 
    return result.json()["translations"][0]["text"]