import requests
import os
import time

from fastapi import FastAPI, Request, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from fastapi.middleware.cors import CORSMiddleware

from Model import SentenceTransformer
from SearchClient import ElasticClient, ElasticQuery
from data import Data

INDEX_SPEC = "vector"
INDEX_NAME = "sgic_search_"
WEBSITE_URL = os.environ.get('WEBSITE_URL', 'http://localhost:9876')
API_URL = WEBSITE_URL+"/api"
APP_KEY = os.environ.get('APP_KEY', '')
CACHE_MIN = int(os.environ.get('CACHE_MIN', 60))
ELASTIC_URL = os.environ.get('ELASTIC_URL', 'http://localhost:9200')

print("Load model")
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
print("Initializing Elastic client")
searchclient = ElasticClient(configs_dir='config/elastic', url=ELASTIC_URL)
dataclass = Data(model, searchclient, config_file="config/attribute.json", setting_file="config/elastic/"+INDEX_SPEC+"_settings.json")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[WEBSITE_URL],
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"]
)

@app.get("/")
@app.get("/api/")
async def root():
    return {"message": "App is running."}

@app.get("/api/search")
@cache(namespace="search", expire=CACHE_MIN*60)
async def search(query: str = '', lang: str = 'de', explain: bool = False):
    time_embed_start = time.time()
    query_vector = searchclient.transform_vector(model.encode(query))
    time_embed = time.time() - time_embed_start

    if explain:
        query_config = ElasticQuery().get_query_densevector_explain(query, query_vector, dataclass.get_relevance(cosine=False), dataclass.get_relevance(cosine=True), dataclass.get_source(), docs_count=1000)
    else:
        query_config = ElasticQuery().get_query_densevector(query, query_vector, dataclass.get_relevance(cosine=False), dataclass.get_relevance(cosine=True), dataclass.get_source(), docs_count=1000, min_score=dataclass.get_minimum_score())

    matches, time_elastic, value, resp = searchclient.query(INDEX_NAME+lang, query_config, explain)
    return {
        "matches": matches,
        "time": {
            "elastic": round(time_elastic/1000, 4),
            "embed": round(time_embed, 4)
        },
        "resp": resp
    }

@app.get("/api/index")
def index(lang: str = 'de', key: str = ''):
    if key == '' or APP_KEY != key:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    print("Read Data")
    #url = API_URL+"/games/"+lang
    url = API_URL+"/"+lang+"/games"
    data_json = requests.get(url).json()

    print("Create Index")
    searchclient.delete_index(INDEX_NAME+lang)
    searchclient.create_index(INDEX_NAME+lang, INDEX_SPEC)

    print("Index Documents")   
    data = dataclass.parse_data(data_json)
    searchclient.index_documents(INDEX_NAME+lang, data)

    return {"message": "Index created."}

@app.get("/api/update")
def update(id: str = '', lang: str = 'de'):
    url = API_URL+"/game/?lang="+lang+"&key="+id
    request = requests.get(url)
    if request.content == b'':
        raise HTTPException(status_code=404, detail="Game "+id+" not found.")
    data_json = request.json()

    print("Index Document")
    data = dataclass.parse_data([data_json])
    searchclient.index_documents(INDEX_NAME+lang, data)
    return {"message": "Document "+id+" updated."}

@app.get("/api/delete")
def delete(id: str = '', lang: str = 'de'):
    searchclient.delete_doc(id, INDEX_NAME+lang)
    return {"message": "Document "+id+" deleted."}

@app.get("/api/get")
def get(id: str = '', lang: str = 'de'):
    document = searchclient.get_doc(id, INDEX_NAME+lang)
    if not document:
        raise HTTPException(status_code=404, detail="Game "+id+" not found.")
    return document

@app.get("/api/similar")
def get(id: str = '', lang: str = 'de', explain: bool = False):
    document = searchclient.get_doc(id, INDEX_NAME+lang)
    if not document:
        raise HTTPException(status_code=404, detail="Game "+id+" not found.")
    
    query_config = ElasticQuery().get_similarity_query(document, dataclass.get_relevance(cosine=False), dataclass.get_relevance(cosine=True), source=dataclass.get_source(), docs_count=10, explain=explain)

    matches, time_elastic, value, resp = searchclient.query(INDEX_NAME+lang, query_config, explain)
    return {
        "matches": matches,
        "time": {
            "elastic": round(time_elastic/1000, 4)
        }
    }

@app.get("/api/clear")
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

  
