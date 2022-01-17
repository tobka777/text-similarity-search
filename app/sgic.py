from .SearchClient.BaseClient import BaseClient
from .Model import BaseModel

def parse_data(data, model: BaseModel, search: BaseClient):
  bulk_size = 1000
  count = 0

  for d in data:
    doc = {
      "id": d["metadataInfo"]["metadataFileIdentifier"],
      "title": d["gameInfo"]["titleInfo"]["title"],
      "title_vec": search.transform_vector(model.encode(d["gameInfo"]["titleInfo"]["title"])),
      "abstract_vec": search.transform_vector(model.encode(d["gameInfo"]["abstract"])),
    }
    yield doc

    count += 1

    if count % bulk_size == 0:
      print("Processed {} documents".format(count))

def get_source():
  return ["id", "title"]

def get_relevance():
  return {
    "title_vec": 2,
    "abstract_vec": 1
  }

def get_minimum_score():
  return sum(get_relevance().values())