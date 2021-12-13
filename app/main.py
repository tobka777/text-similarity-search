from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
import requests

from datetime import datetime

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/search")
@cache(namespace="search", expire=2000) # cache in seconds
async def search(query: str = '', lang: str = ''):
    return datetime.now()

@app.get("/clear")
async def clear():
    return await FastAPICache.clear(namespace="search")

@app.get("/index")
async def index(url: str = ''):
    #secure endpoint, delete index, clean cache
    data = requests.get(url).json()
    return data

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

  