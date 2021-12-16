from contextlib import nullcontext
from fastapi import FastAPI, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
import requests

import time

from .Model import Word2Vec
from .Model import SentenceTransformer
from .SearchClient import ElasticClient, ElasticQuery
from .sgic import parse_data

app = FastAPI()
print("Load model")
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
print("Initializing Elastic client")
searchclient = ElasticClient(configs_dir='config/elastic')

INDEX_SPEC = "vector"
INDEX_NAME = "sgic_search"

@app.get("/")
async def root():
    return {"message": "App is running."}

@app.get("/search")
#@cache(namespace="search", expire=2000) # cache in seconds
async def search(query: str = '', lang: str = 'de'):
    time_embed_start = time.time()
    query_vector = searchclient.transform_vector(model.encode(query))
    time_embed = time.time() - time_embed_start

    print(len(query_vector))

    relevance = {
        "title_vec": 2,
        "abstract_vec": 1
    }
    source = ["id", "title"]

    query_config = ElasticQuery().get_query_densevector(query_vector, relevance, source, 10)
    matches, time_elastic, value = searchclient.query(INDEX_NAME, query_config)
    return {
        "matches": matches,
        "time": {
            "elastic": round(time_elastic/1000, 4),
            "embed": round(time_embed, 4)
        }
    }

@app.get("/clear")
async def clear():
    return await FastAPICache.clear(namespace="search")

@app.get("/index")
def index(lang: str = 'de'):
    time_start = time.time()
    # background task, https://testdriven.io/blog/fastapi-and-celery/
    #secure endpoint, delete index, clean cache
    print("Read Data")
    url = "https://seriousgames-portal.org/api/games/de"
    data_json = requests.get(url).json()

    print("Create Index")
    searchclient.delete_index(INDEX_NAME)
    searchclient.create_index(INDEX_NAME, INDEX_SPEC)

    print("Index Documents")   
    data = parse_data(data_json, model, searchclient)
    searchclient.index_documents(INDEX_NAME, data)

    return {"message": "Index created."}

@app.get("/update")
def update(id: str = '', lang: str = 'de'):
    #PUT http://localhost:9200/sgic_search/_doc/bf5e5e08-3b8d-4f34-bdc6-0c74be2e3065 -> JSON vom Dokument
    #check if found true, else bulk
    
    ####get only selected game####
    #id = "bf5e5e08-3b8d-4f34-bdc6-0c74be2e3065"
    #url = "https://seriousgames-portal.org/api/game/?lang=de&key="+id
    #data_json = requests.get(url).json()

    ####only testing####
    url = "https://seriousgames-portal.org/api/games/de"
    data_json = requests.get(url).json()[0]

    print("Index Document")
    data = parse_data([data_json], model, searchclient)
    searchclient.index_documents(INDEX_NAME, data)
    return {"message": "Document "+id+" updated."}

@app.get("/delete")
def update(id: str = ''):
    searchclient.delete_doc(id, INDEX_NAME)
    return {"message": "Document "+id+" deleted."}

@app.get("/get")
def get(id: str = '', lang: str = 'de'):
    return searchclient.get_doc(id, INDEX_NAME)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time, 4))
    return response

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

  