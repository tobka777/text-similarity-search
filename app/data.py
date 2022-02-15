from numpy import array
from SearchClient.BaseClient import BaseClient
from Model import BaseModel
import json
from functools import reduce

class Data:
  def __init__(self, model: BaseModel, search: BaseClient):
    self.model = model
    self.search = search
    attrjson = self.load_config('attribute')
    relevance = {}
    source = []
    attribute = []
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
      if "name" not in attr:
        name = attr["attribute"].replace(".[*]", "").replace(".[]", "").replace(".", "_").replace("*", "all")
        attr["name"] = name+"_vec" if attr["vector"] else name
      if "source" not in attr:
        attr["source"] = False
      attribute.append(attr)

      relevance[attr["name"]] = attr["score"]
      if attr["source"]:
        source.append(attr["name"])

    self.relevance = relevance
    self.source = source
    self.attribute = attribute
    print(attribute)

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
    with open('config/'+file+'.json', 'r') as f:
      return json.load(f)

  def parse_data(self, data):
    bulk_size = 1000
    count = 0
    joinString = " , "

    for d in data:
      doc = {}

      valueValid = True
      for attr in self.attribute:
        if not attr:
          continue

        value = d
        for id in attr["attribute"].split("."):
          valueValid = True

          if id == '*':
            #JSON Values
            JsonValues = self.get_all_values(value, [])
            value = joinString.join([v for v in list(set(JsonValues)) if v != None and v.strip() != '' and v != 'none'])
            break

          elif isinstance(value, list):
            #list of values
            print(attr["attribute"])
            print(id)
            if id == '[]':
              #array list
              value = joinString.join(list(set(value)))
              break
            elif id == '[*]':
              #object, jump to object value in next loop
              continue
            else:
              #combine object value
              tmpval = []
              for val in value:
                if id in val:
                  tmpval.append(val[id])
                else:
                  print("ERROR: "+str(id)+" not exists")
              value = joinString.join(list(set(tmpval)))
              break

          else:
            #specific value
            if id not in value:
              valueValid = False
              print("ERROR: "+str(id)+" not exists")
              break
            value = value[id]

        if valueValid:
          self.transform(attr["name"], value, doc, attr["vector"])

      yield doc

      count += 1

      if count % bulk_size == 0:
        print("Processed {} documents".format(count))

  def get_source(self):
    return self.source

  def get_relevance(self):
    return self.relevance

  def get_minimum_score(self):
    values = self.relevance.values()
    return sum(values)/len(values)

