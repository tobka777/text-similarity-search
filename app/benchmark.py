from Benchmark import SICK, STSB
from Model import SentenceTransformer, FastText, Bert, Spacy, mUSE, LASER, SIF, Gensim

def benchmark_run_print(benchmark, lang, model):
  test = model.encode("Test")
  print(test.shape)
  (pearson, spearman, embed_time) = benchmark.run(model, lang)
  #model; benchmark; pearson; spearman; time for embed avg; min; max)
  return str(model.name)+";"+str(type(benchmark).__name__)+";"+str(lang)+";"+str(pearson)+";"+str(spearman)+";"+str(embed_time[0])+";"+str(embed_time[1])+";"+str(embed_time[2])+";"+str(len(test))

"""
#Baseline
model = FastText('cc.en.300.bin')
model = FastText('cc.de.300.bin')
model = Spacy("en_core_web_lg")
model = Spacy("de_core_news_lg")
model = SIF("en_core_web_lg")
model = SIF("de_core_news_lg")
model = Gensim('word2vec-google-news-300')

#BERT
model = Bert('bert-base-multilingual-cased')
model = Bert('bert-base-cased')
model = Bert('bert-base-german-cased')

#SBERT
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
model = SentenceTransformer('paraphrase-xlm-r-multilingual-v1')
model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
model = SentenceTransformer('sentence-transformers/LaBSE')
model = mUSE('mUSE')
model = LASER('LASER')
"""

model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

#print(benchmark_run_print(STSB(), 'en', model))
#print(benchmark_run_print(STSB(), 'de', model))
#print(benchmark_run_print(SICK(), 'en', model))
print(benchmark_run_print(SICK(), 'de', model))

