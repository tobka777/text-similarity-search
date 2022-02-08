import os
import requests
import json
from .BaseClient import BaseClient
import elasticsearch.helpers
from elasticsearch import Elasticsearch
import re

class ElasticResp:
    def __init__(self, resp):
        self.status_code = 400
        if 'acknowledged' in resp and resp['acknowledged']:
            print("request acknowledged!")
            self.status_code = 200
        else:
            self.status_code = resp['status']
            self.text = json.dumps(resp, indent=2)


class BulkResp():
    def __init__(self, resp):
        self.status_code = 400
        if resp[0] > 0:
            self.status_code = 201


class SearchResp():
    def __init__(self, resp):
        self.status_code = 400
        if 'hits' in resp:
            self.status_code = 200
        else:
            self.status_code = resp['status']
            self.text = json.dumps(resp, indent=2)


class ElasticClient(BaseClient):
    """ Note on the Elastic client,
        Elastic LTR is not bound to an index like Solr LTR
        so many calls take an index but do not use it

        In the future, we may wish to isolate an Index's feature
        store to a feature store of the same name of the index
    """
    def __init__(self, host=None, configs_dir='.', https=False, port=9200):
        self.docker = os.environ.get('LTR_DOCKER') != None
        self.configs_dir = configs_dir #location of elastic configs
        self.port = port

        # respect host if it is set
        if host is not None:
            self.host = host
        else:
            if self.docker:
                self.host = 'elastic'
            else:
                self.host = 'localhost'

        if https:
            self.protocol = "https"
        else:
            self.protocol = "http"
        
        self.elastic_ep = '{}://{}:{}/_ltr'.format(self.protocol, self.host, self.port)
        self.es = Elasticsearch('{}://{}:{}'.format(self.protocol, self.host, self.port))

    def get_host(self):
        return self.host

    def name(self):
        return "elastic"

    def resp_msg(self, msg, resp, throw=True):
        print('{} [Status: {}]'.format(msg, resp.status_code))
        if resp.status_code >= 400:
            print(resp.text)
            if throw:
                raise RuntimeError(resp.text)

    def delete_index(self, index):
        resp = self.es.indices.delete(index=index, ignore=[400, 404], ignore_unavailable=True)
        self.resp_msg("Deleted index {}".format(index), ElasticResp(resp))

    def create_index(self, index_name, index_spec):
        """ Take the local config files for Elasticsearch for index, reload them into ES"""
        cfg_json_path = os.path.join(self.configs_dir, "%s_settings.json" % index_spec)
        with open(cfg_json_path) as src:
            settings = json.load(src)
            resp = self.es.indices.create(index_name, body=settings)
            print("create_index: resp={}".format(resp))
            self.resp_msg("Created index {}".format(index_name), ElasticResp(resp))

    def index_documents(self, index, doc_src):

        def bulkDocs(doc_src):
            for doc in doc_src:
                if 'id' not in doc:
                    raise ValueError("Expecting docs to have field 'id' that uniquely identifies document")
                addCmd = {"_index": index,
                          "_id": doc['id'],
                          "_source": doc}
                yield addCmd

        resp = elasticsearch.helpers.bulk(self.es, bulkDocs(doc_src), chunk_size=100)
        self.es.indices.refresh(index=index)
        self.resp_msg(msg="Streaming Bulk index DONE {}".format(index), resp=BulkResp(resp))

    def reset_ltr(self):
        resp = requests.delete(self.elastic_ep)
        self.resp_msg(msg="Removed Default LTR feature store".format(), resp=resp, throw=False)
        resp = requests.put(self.elastic_ep)
        self.resp_msg(msg="Initialize Default LTR feature store".format(), resp=resp)

    def create_featureset(self, name, ftr_config):
        resp = requests.post('{}/_featureset/{}'.format(self.elastic_ep, name), json=ftr_config)
        self.resp_msg(msg="Create {} feature set".format(name), resp=resp)

    def log_query(self, index, featureset, ids, params={}):
        params = {
            "query": {
                "bool": {
                    "filter": [
                        {
                            "sltr": {
                                "_name": "logged_features",
                                "featureset": featureset,
                                "params": params
                            }
                        }
                    ]
                }
            },
            "ext": {
                "ltr_log": {
                    "log_specs": {
                        "name": "ltr_features",
                        "named_query": "logged_features"
                    }
                }
            },
            "size": 1000
        }

        terms_query = [
            {
                "terms": {
                    "_id": ids
                }
            }
        ]

        if ids is not None:
            params["query"]["bool"]["must"] = terms_query

        resp = self.es.search(index=index, body=params)
        self.resp_msg(msg="Searching {} - {}".format(index, str(terms_query)[:20]), resp=SearchResp(resp))

        matches = []
        for hit in resp['hits']['hits']:
            hit['_source']['ltr_features'] = []

            for feature in hit['fields']['_ltrlog'][0]['ltr_features']:
                value = 0.0
                if 'value' in feature:
                    value = feature['value']

                hit['_source']['ltr_features'].append(value)

            matches.append(hit['_source'])

        return matches

    def submit_model(self, featureset, model_name, model_payload):
        model_ep = "{}/_model/".format(self.elastic_ep)
        create_ep = "{}/_featureset/{}/_createmodel".format(self.elastic_ep, featureset)

        resp = requests.delete('{}{}'.format(model_ep, model_name))
        print('Delete model {}: {}'.format(model_name, resp.status_code))

        resp = requests.post(create_ep, json=model_payload)
        self.resp_msg(msg="Created Model {}".format(model_name), resp=resp)

    def submit_ranklib_model(self, featureset, index, model_name, model_payload):
        params = {
            'model': {
                'name': model_name,
                'model': {
                    'type': 'model/ranklib',
                    'definition': model_payload
                }
            }
        }
        self.submit_model(featureset, index, model_name, params)

    def model_query(self, index, model, model_params, query):
        params = {
            "query": query,
            "rescore": {
                "window_size": 1000,
                "query": {
                    "rescore_query": {
                        "sltr": {
                            "params": model_params,
                            "model": model
                        }
                    }
                }
            },
            "size": 1000
        }

        resp = self.es.search(index=index, body=params)
        self.resp_msg(msg="Searching {} - {}".format(index, str(query)[:20]), resp=SearchResp(resp))

        # Transform to consistent format between ES/Solr
        matches = []
        for hit in resp['hits']['hits']:
            matches.append(hit['_source'])

        return matches

    def query(self, index, query, explain: False):
        print("query:{}".format(query))
        resp = self.es.search(index=index, body=query)
        self.resp_msg(msg="Searching {} - {}".format(index, str(query)[:20]), resp=SearchResp(resp))

        #print("================ ES response")
        #print(resp)

        # Transform to consistent format between ES/Solr
        matches = []
        for hit in resp['hits']['hits']:
          hit['_source']['_score'] = hit['_score']
          if explain:
            hit['_source']['scores'] = ElasticQuery().explain_scores(hit)
          matches.append(hit['_source'])

        return matches, resp['took'], resp['hits']['total']['value']

    def feature_set(self, index, name):
        resp = requests.get('{}/_featureset/{}'.format(self.elastic_ep,
                                                      name))

        jsonResp = resp.json()
        if not jsonResp['found']:
            raise RuntimeError("Unable to find {}".format(name))

        self.resp_msg(msg="Fetched FeatureSet {}".format(name), resp=resp)

        rawFeatureSet = jsonResp['_source']['featureset']['features']

        mapping = []
        for feature in rawFeatureSet:
            mapping.append({'name': feature['name']})

        return mapping, rawFeatureSet

    def get_doc(self, doc_id, index):
        resp = self.es.get(index=index, id=doc_id)
        #self.resp_msg(msg="Fetched Doc {}".format(doc_id), resp=resp, throw=False)
        return resp['_source']

    def transform_vector(self, vector):
        return vector.flatten().tolist()

    def delete_doc(self, doc_id, index):
        resp = self.es.delete(index=index, id=doc_id, ignore=[400, 404])
        #self.resp_msg(msg="Deleted Doc {}".format(doc_id), resp=resp, throw=False)

class ElasticQuery():
    def get_query_basic(self, query):
        return {
            "query": query
        }

    def get_query_densevector(self, query_vector, relevance_json, source=None, docs_count=None, min_score=None):
        query = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": self.get_distance_metric(relevance_json),
                        "params": {"query_vector": query_vector}
                    }
                }
            }
        }
        if min_score is not None:
          query['query']['script_score']['min_score'] = min_score
        if docs_count is not None:
          query['size'] = docs_count
        if source is not None:
          query['_source'] = source

        return query

    def get_distance_value(self, attribute, boost):
      return "doc['"+attribute+"'].size() == 0 ? 0 : (cosineSimilarity(params.query_vector, '"+attribute+"') + 1.0) * "+str(boost)

    def get_distance_metric(self, relevance_json):
      metric = []
      for attribute, boost in relevance_json.items():
        metric.append(self.get_distance_value(attribute, boost))
      metric.append('_score')
      return ' + '.join(metric)

    def explain_scores(self, hit):
      scores = []
      if '_explanation' in hit and 'details' in hit['_explanation']:
        for detail in hit['_explanation']['details']:
          if 'value' in detail and 'description' in detail:
            template = {
              "score": detail['value'],
              "script": detail['description']
            }
            script = re.search("idOrCode='(.*)'", detail['description'])
            if script and len(script.groups()) >= 1:
              template["script"] = script.group(1)
              values = re.search("'(\w*)'.*\*\s(\d+\.?\d*)", template["script"])
              if values and len(values.groups()) >= 2:
                template["attribute"] = values.group(1)
                template["boost"] = float(values.group(2))
                template["score"] = float(template["score"])/float(values.group(2))
            scores.append(template)
        scores = sorted(scores, key=lambda k: k['score'], reverse=True)
      return scores

    def get_query_densevector_explain(self, query_vector, relevance_json, source):
        script_score = []
        #"boost": boost
        for attribute, boost in relevance_json.items():
          template = {
            "script_score": {
              "query": {"match_all": {}},
              "script": {
                "source": self.get_distance_value(attribute, boost),
                "params": {"query_vector": query_vector}
              }
            }
          }
          script_score.append(template)

        script_score.append({
          "script_score": {
            "query": {"match_all": {}},
            "script": {
              "source": "_score"
            }
          }
        })

        return {
            "explain": True,
            "_source": source,
            "query": {
                "bool": {
                    "should": script_score
                }
            }
        }