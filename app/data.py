from numpy import array
from SearchClient.BaseClient import BaseClient
from Model import BaseModel
import json
from functools import reduce

class Data:
  SEARCH_NORMAL="search_normal"
  SEARCH_COSINE="search_cosine"
  SIMILAR_NORMAL="similar_normal"
  SIMILAR_COSINE="similar_cosine"

  def __init__(self, model: BaseModel, search: BaseClient, config_file, setting_file):
    self.model = model
    self.search = search
    attrjson = self.load_config(config_file)
    relevance = {self.SEARCH_NORMAL: {}, self.SEARCH_COSINE: {}, self.SIMILAR_NORMAL: {}, self.SIMILAR_COSINE: {}}
    source = []
    attribute = []
    settings = {}
    for attr in attrjson:
      #required
      if "attribute" not in attr:
        print("attribute is required")
        return False

      #optional values with default value
      if "score" not in attr:
        attr["score"] = 0
      if "vector" not in attr:
        attr["vector"] = True
      if "similar" not in attr:
        attr["similar"] = True
      if "name" not in attr:
        name = attr["attribute"].replace(".[*]", "").replace(".[]", "").replace(".", "_").replace("*", "all")
        attr["name"] = name+"_vec" if attr["vector"] else name
      if "source" not in attr:
        attr["source"] = False
      attribute.append(attr)

      if attr["score"] > 0:
        if attr["vector"]:
          relevance[self.SEARCH_COSINE][attr["name"]] = attr["score"]
          if attr["similar"]:
            relevance[self.SIMILAR_COSINE][attr["name"]] = attr["score"]
        else:
          relevance[self.SEARCH_NORMAL][attr["name"]] = attr["score"]
          if attr["similar"]:
            relevance[self.SIMILAR_NORMAL][attr["name"]] = attr["score"]
      if attr["source"]:
        source.append(attr["name"])

      if attr["vector"]:
        settings[attr["name"]] = {"type": "dense_vector", "dims": 768}
      elif attr["name"] == 'id':
        settings[attr["name"]] = {"type": "keyword"}
      else:
        settings[attr["name"]] = {"type": "text"}

    self.relevance = relevance
    self.source = source
    self.attribute = attribute

    settings_json = {
      "settings": {
        "number_of_shards": 2,
        "number_of_replicas": 0
      },
      "mappings": {
        "dynamic": "false",
        "_source": {
          "enabled": "true"
        },
        "properties": settings
      }
    }
    self.write_config(settings_json, setting_file)

  def transform(self, name, value, doc, vector=True):
    if vector:
      if value.strip() != '':
        doc[name] = self.search.transform_vector(self.model.encode(value.strip()))
    else:
      doc[name] = value.strip()

  def get_all_values(self, obj, arr):
    """Recursively search for values of key in JSON tree."""
    if isinstance(obj, dict):
      for k, v in obj.items():
        if isinstance(v, (dict, list)):
          self.get_all_values(v, arr)
        else:
          #print(k, ":", v)
          arr.append(v)
    elif isinstance(obj, list):
      for item in obj:
        self.get_all_values(item, arr)
    return arr

  def load_config(self, file):
    with open(file, 'r') as f:
      return json.load(f)

  def write_config(self, dictionary, filename):
    json_object = json.dumps(dictionary, indent = 4)
    with open(filename, "w") as outfile:
      outfile.write(json_object)

  def parse_data(self, data):
    bulk_size = 1000
    count = 0
    join_string = " , "

    for d in data:
      doc = {}

      value_valid = True
      for attr in self.attribute:
        if not attr:
          continue

        value = d
        for id in attr["attribute"].split("."):
          value_valid = True

          if id == '*':
            #JSON Values
            json_values = self.get_all_values(value, [])
            value = join_string.join([v for v in list(set(json_values)) if v != None and v.strip() != '' and v != 'none'])
            break

          elif isinstance(value, list):
            #list of values
            print(attr["attribute"])
            print(id)
            if id == '[]':
              #array list
              value = join_string.join(list(set(value)))
              break
            elif id == '[*]':
              #object, jump to object value in next loop
              continue
            else:
              #combine object value
              tmp_val = []
              for val in value:
                if id in val:
                  tmp_val.append(val[id])
                else:
                  print("ERROR: "+str(id)+" not exists")
              value = join_string.join(list(set(tmp_val)))
              break

          else:
            #specific value
            if id not in value:
              value_valid = False
              print("ERROR: "+str(id)+" not exists")
              break
            value = value[id]

        if value_valid:
          self.transform(attr["name"], value, doc, attr["vector"])

      yield doc

      count += 1

      if count % bulk_size == 0:
        print("Processed {} documents".format(count))

  def get_source(self):
    return self.source

  def get_relevance(self, relevance_type):
    return self.relevance[relevance_type]

  def get_minimum_score(self):
    val1 = self.get_relevance(True).values()
    val2 = self.get_relevance(False).values()
    return (sum(val1)+sum(val2))/(len(val1)+len(val2))

