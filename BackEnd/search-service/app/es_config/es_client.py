import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch_dsl import connections

load_dotenv()

connections.create_connection(hosts=[os.getenv("ELASTICSEARCH_HOST", 'http://elasticsearch:9200')])

es = Elasticsearch(hosts=[os.getenv("ELASTICSEARCH_HOST", 'http://elasticsearch:9200')])
