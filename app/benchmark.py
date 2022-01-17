from Benchmark import SICK, STSB
from Model import SentenceTransformer, FastText, Bert, Spacy, LaBSE, mUSE, LASER, XLR

"""
#Baseline
model = FastText('cc.en.300.bin')
model = FastText('cc.de.300.bin')
model = Spacy("en_core_web_lg")
model = Spacy("de_core_news_lg")

#BERT
model = Bert('bert-base-multilingual-cased')
model = Bert('bert-base-cased')
model = Bert('bert-base-german-cased')

#SBERT
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
model = SentenceTransformer('paraphrase-xlm-r-multilingual-v1')
model = LaBSE('LaBSE')
model = mUSE('mUSE')
model = LASER('LASER')
model = XLR('XLR')
"""

#model = FastText('cc.en.300.bin')
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

def benchmark_run_print(benchmark, lang):
  (pearson, spearman, embed_time) = benchmark.run(model, lang)
  #model; benchmark; pearson; spearman; time for embed avg; min; max)
  return model.name+";"+type(benchmark).__name__+" "+lang+";"+pearson+";"+spearman+";"+embed_time[0]+";"+embed_time[1]+";"+embed_time[2]

print(benchmark_run_print(STSB(), 'en'))
print(benchmark_run_print(STSB(), 'de'))
print(benchmark_run_print(SICK(), 'en'))


