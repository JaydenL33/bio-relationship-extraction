from elasticsearch import Elasticsearch
es_client = Elasticsearch("http://localhost:9200")
index_name = "my_index_hybrid"
settings = {
    "analysis": {
        "analyzer": {
            "ngram_analyzer": {
                "tokenizer": "ngram_tokenizer",
                "filter": ["lowercase"]
            }
        },
        "tokenizer": {
            "ngram_tokenizer": {
                "type": "ngram",
                "min_gram": 3,
                "max_gram": 5,
                "token_chars": ["letter", "digit"]
            }
        }
    }
}
mappings = {
    "properties": {
        "text": {
            "type": "text",
            "analyzer": "ngram_analyzer",
            "search_analyzer": "standard"
        },
        "dense_vector": {
            "type": "dense_vector",
            "dims": 1024  # BGE-m3 produces 1024-dim vectors
        }
    }
}
es_client.indices.create(index=index_name, body={"settings": settings, "mappings": mappings})