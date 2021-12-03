from elasticsearch import Elasticsearch
import os
import json

class ElasticLoader:
    def __init__(self, host="http://localhost", port=9200):
        try:
            self.es = Elasticsearch(HOST=host, PORT=port)
        except RuntimeError:
            print("Connection failed")
            exit()

    @staticmethod
    def get_json(url):
        return {}

    def add_by_json(self, d, index="github", doc_type=None, id_=None):  # requires dictionary with description of repository
        self.es.index(index=index, doc_type=doc_type, id=id_, document=d)

    def add_by_url(self, url):
        self.add_by_json(self.get_json(url))

    def add_by_url_list(self, l):
        for url in l:
            try:
                json = self.get_json(l)
                self.add_by_json(json)
            except RuntimeError:
                return 1
        return 0

    def pop(self, id_):
        pass

    def get(self):  # parameters ???
        pass


class DirectoryLoader:
    def __init__(self):

        for filename in os.listdir('data'):
            if filename.endswith(".json"):
                path = os.path.join('data', filename)
                f = open(path)
                dt = json.load(f)
                print("-" * 20 + '\n', dt)
                continue


c = DirectoryLoader()
