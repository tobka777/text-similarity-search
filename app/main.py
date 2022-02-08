import requests
import os
import time

from fastapi import FastAPI, Request
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from fastapi.middleware.cors import CORSMiddleware

from .Model import SentenceTransformer
from .SearchClient import ElasticClient, ElasticQuery
from .sgic import parse_data, get_relevance, get_source

INDEX_SPEC = "vector"
INDEX_NAME = "sgic_search_"
WEBSITE_URL = os.environ.get('WEBSITE_URL', 'http://localhost:9876')
API_URL = WEBSITE_URL+"/api"
APP_KEY = os.environ.get('APP_KEY', '')
CACHE_MIN = os.environ.get('CACHE_MIN', 60)

print("Load model")
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
print("Initializing Elastic client")
searchclient = ElasticClient(configs_dir='config/elastic')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEBSITE_URL],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "App is running."}

@app.get("/search")
@cache(namespace="search", expire=CACHE_MIN*60)
async def search(query: str = '', lang: str = 'de', explain: bool = False):
    time_embed_start = time.time()
    query_vector = searchclient.transform_vector(model.encode(query))
    time_embed = time.time() - time_embed_start

    if explain:
        query_config = ElasticQuery().get_query_densevector_explain(query_vector, get_relevance(), get_source())
    else:
        query_config = ElasticQuery().get_query_densevector(query_vector, get_relevance(), get_source(), docs_count=1000)

    matches, time_elastic, value = searchclient.query(INDEX_NAME+lang, query_config, explain)
    return {
        "matches": matches,
        "time": {
            "elastic": round(time_elastic/1000, 4),
            "embed": round(time_embed, 4)
        }
    }

@app.get("/index")
def index(lang: str = 'de', key: str = ''):
    if key == '' or APP_KEY != key:
        #TODO send ERROR code
        return {"message": "Unauthorized."}

    print("Read Data")
    url = API_URL+"/games/"+lang
    data_json = requests.get(url).json()

    print("Create Index")
    searchclient.delete_index(INDEX_NAME+lang)
    searchclient.create_index(INDEX_NAME+lang, INDEX_SPEC)

    print("Index Documents")   
    data = parse_data(data_json, model, searchclient)
    searchclient.index_documents(INDEX_NAME+lang, data)

    return {"message": "Index created."}

@app.get("/update")
def update(id: str = '', lang: str = 'de'):
    url = API_URL+"/game/?lang="+lang+"&key="+id
    request = requests.get(url)
    if request.content == b'':
        return {"message": "Game "+id+" not found."}
    data_json = request.json()

    print("Index Document")
    data = parse_data([data_json], model, searchclient)
    searchclient.index_documents(INDEX_NAME+lang, data)
    return {"message": "Document "+id+" updated."}

@app.get("/delete")
def delete(id: str = '', lang: str = 'de'):
    searchclient.delete_doc(id, INDEX_NAME+lang)
    return {"message": "Document "+id+" deleted."}

@app.get("/get")
def get(id: str = '', lang: str = 'de'):
    return searchclient.get_doc(id, INDEX_NAME+lang)

@app.get("/clear")
async def clear():
    return await FastAPICache.clear(namespace="search")

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

  