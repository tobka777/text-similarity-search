# SearchAPI - Text Similarity Search

SearchAPI is a library for a semantic similarity search. This API creates the representations of the search queries and the attributes of the documents using a chosen text similarity method. Depending on the configuration, the vector representation or the text of an attribute is used to create the index of the documents. A search query requests a search server such as Elasticsearch, which uses an appropriate distance measure and a score function to determine a similarity value and use it to rank the results.
As an example, the SearchAPI was adapted for the web-based information system for serious games SG-IC (see [config/attribute.json](https://github.com/tobka777/text-similarity-search/blob/main/config/attribute.json) and [.env.example](https://github.com/tobka777/text-similarity-search/blob/main/.env.example)).

## Installation
```
$ git clone https://github.com/tobka777/text-similarity-search.git
$ cd text-similarity-search
$ cp .env.example .env
$ docker-compose up -d --build
```

## Configuration
### .env / [.env.example](https://github.com/tobka777/text-similarity-search/blob/main/.env.example)
- `WEBSITE_URL`: URL of the web page that provides the resources (default: http://localhost:3000)
- `RESOURCE_PATH_ALL`: Path to get all resources as JSON (default: `/api/{lang}/`)
    - `{lang}`: language iso 
- `RESOURCE_PATH_ALL`: Path to get specific resources by id as JSON (default: `RESOURCE_PATH_ALL`+`/{id}`) 
    - `{lang}`: language iso 
    - `{id}`: id of resource 
- `ELASTIC_URL`: URL of the Elasticsearch cluster (default: http://localhost:9200)
- `APP_KEY`: Key as a protection of the index creation
- `CACHE_MIN`: Duration of the caching (in memory) of the search queries in minutes (default: 60 min)
- `MIN_SCORE`: fixed minimum score (default: sum of all weights of the attributes in vector representation)
- `INDEX_NAME`: Prefix for the index on Elasticsearch (default: index_)

### [attribute.json](https://github.com/tobka777/text-similarity-search/blob/main/config/attribute.json)
The JSON array contains an object with the following values for each attribute to be considered.
- `attribute`: path in JSON like `gameInfo.titleInfo.title` (`.`: object; `[]`: array; `[*]`: array of objects; `*`: all values of an object)
- `boost`: weighting of the attribute (default: `0` - no boost)
- `vector`: `true` if saved as vector representation and `false` if saved as text (default: `true`)
- `name`: alternative name if not to be derived from attributes (default: `attribute`)
- `source`: Attributes to be returned on result (default: `false`)
- `search`: Attributes to be taken into account during search (default: `true`)
- `similar`: Attributes to be considered when comparing similarity between documents (default: `false`)
- `similar_boost`: Alternative weighting for similarity comparison between documents (default: `boost`)

## Contributing
Pull requests are welcome. For major changes, please open an [issue](https://github.com/tobka777/text-similarity-search/issues) first to discuss what you would like to change.

## License

Distributed under the Apache 2.0 License. See [LICENSE](https://github.com/tobka777/text-similarity-search/blob/main/LICENCE) for more information.

