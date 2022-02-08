import os
import time
import requests

from sgic import parse_data
from celery import Celery

INDEX_SPEC = os.environ.get('INDEX_SPEC', 'vector')
INDEX_NAME = os.environ.get('INDEX_NAME', 'sgic_search_')
WEBSITE_URL = os.environ.get('WEBSITE_URL', 'http://localhost:9876')
API_URL = WEBSITE_URL+"/api"
APP_KEY = os.environ.get('APP_KEY', '')
CACHE_MIN = os.environ.get('CACHE_MIN', 60)

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

@celery.task(name="create_index")
def create_index(searchclient, model, lang):
    print("Read Data")
    url = API_URL+"/games/"+lang
    data_json = requests.get(url).json()

    print("Create Index")
    searchclient.delete_index(INDEX_NAME+lang)
    searchclient.create_index(INDEX_NAME+lang, INDEX_SPEC)

    print("Index Documents")   
    data = parse_data(data_json, model, searchclient)
    searchclient.index_documents(INDEX_NAME+lang, data)

    return "Index created."