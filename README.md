# SearchAPI

## Elasticsearch

docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.14.1

## Solr
Before running preprocessing / indexing, you need to configure the vector plugin, which allows to index and query the vector data.
You can find the plugin for Solr 8.x here: https://github.com/DmitryKey/solr-vector-scoring

After the plugin's jar has been added, configure it in the solrconfig.xml like so:
    <queryParser name="vp" class="com.github.saaay71.solr.VectorQParserPlugin" />

Schema also requires an addition: field of type `VectorField` is required in order to index vector data:
    <field name="vector" type="VectorField" indexed="true" termOffsets="true" stored="true" termPositions="true" termVectors="true" multiValued="true"/>

## Deployment

docker-compose up -d --build

