from numpy import array
from SearchClient.BaseClient import BaseClient
from Model import BaseModel
import json
import operator
from functools import reduce

def parse_data(data, model: BaseModel, search: BaseClient):
  bulk_size = 1000
  count = 0

  def transform(name, value, doc, vector=True):
    if vector:
      if value.strip() != '':
        doc[name] = search.transform_vector(model.encode(value.strip()))
    else:
      doc[name] = value.strip()

  def get_all_values(obj, arr):
    """Recursively search for values of key in JSON tree."""
    if isinstance(obj, dict):
      for k, v in obj.items():
        if isinstance(v, (dict, list)):
          get_all_values(v, arr)
        else:
          #print(k, ":", v)
          arr.append(v)
    elif isinstance(obj, list):
      for item in obj:
        get_all_values(item, arr)
    return arr

  joinString = " , "
  attribute = load_config('attribute')
  for d in data:
    doc = {
      "id": d["gameInfo"]["titleInfo"]["gameID"],
      "title": d["gameInfo"]["titleInfo"]["title"],
    }

    valueValid = True
    for attr in attribute:
      #required
      if "attribute" not in attr:
        continue

      #optional values with default value
      if "score" not in attr:
        attr["score"] = 0
      if "vector" not in attr:
        attr["vector"] = True
      if "name" not in attr:
        attr["name"] = get_name(attr["attribute"], attr["vector"])

      value = d
      for id in attr["attribute"].split("."):
        valueValid = True

        if id == '*':
          #JSON Values
          JsonValues = get_all_values(value, [])
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
        transform(attr["name"], value, doc, attr["vector"])

    yield doc

    count += 1

    if count % bulk_size == 0:
      print("Processed {} documents".format(count))

def get_name(attribute, vector=True):
  name = attribute.replace(".[*]", "").replace(".[]", "").replace(".", "_").replace("*", "all")
  return name+"_vec" if vector else name

def get_source():
  return ["id", "title"]

def get_relevance():
  attribute = load_config('attribute')
  result = {}
  for attr in attribute:
    if "attribute" not in attr:
      continue
    if "score" not in attr:
      attr["score"] = 0
    if "vector" not in attr:
        attr["vector"] = True
    if "name" not in attr:
      attr["name"] = get_name(attr["attribute"], attr["vector"])

    result.update({attr["name"]: attr["score"]})
  return result 

def get_minimum_score():
  return sum(get_relevance().values())

def load_config(file):
  with open('config/'+file+'.json', 'r') as f:
    return json.load(f)