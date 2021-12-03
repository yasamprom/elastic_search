import json
import os
from elasticsearch import Elasticsearch
from elasticsearch import exceptions as elasticerrors


class ElasticLoader:
    index_ = "similar_projects"

    def __init__(self, host="http://localhost", port=9200):
        try:
            self.es = Elasticsearch(HOST=host, PORT=port)
        except RuntimeError:
            print("Connection failed")
            exit()

    def create_index(self, directory='.', index=index_, doc_type=None, ind=1):
        # mapping = {'mappings': {'properties': {
        # 'name': {'type': 'keyword'},
        # 'languages': {'type': 'keyword'},
        # 'percentages': {'type': 'keyword'},
        # 'imports': {'type': 'text'}
        # }}}
        try:
            self.es.indices.create(index=index)
            for filename in os.listdir(directory):
                path = os.path.join('data', filename)
                if filename.endswith('.json'):
                    doc = json.load(open(path))
                    self.add_by_json(d=doc, index=index, doc_type=doc_type, id_=ind)
                    ind += 1
        except elasticerrors.ElasticsearchException:
            print("Index already exists")
            exit()

    @staticmethod
    def get_json(url):
        return {}

    def add_by_json(self, d, index=index_, doc_type=None,
                    id_=None):  # requires dictionary with description of repository
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

    def delete_index(self, index=index_):
        try:
            if input(("Delete index? Y/n: ")) == "Y":
                self.es.indices.delete(index=index)
        except elasticerrors.NotFoundError:
            print("Index does not exist")
            exit()

    def update_index(self, index=index_, doc_type=None, start=1, path='.'):
        self.delete_index(index=index)
        self.create_index(index=index, doc_type=doc_type, start=start, path=path)

    def search(self, d, index='github', limit=3):
        search_arr = list()

        if 'languages' in d.keys():
            for language in d['languages']:
                search_arr.append({'index': index})
                search_arr.append({"query": {"match_phrase": {"languages": language}}, 'from': 0, 'size': limit})
        if 'percentages' in d.keys():
            pass
        if 'imports' in d.keys():
            for import_ in d['imports']:
                search_arr.append({'index': index})
                search_arr.append({"query": {"match_phrase": {"imports": import_}}, 'from': 0, 'size': limit})

        request = ''
        for each in search_arr:
            request += '%s \n' % json.dumps(each)
        print(request)
        resp = self.es.msearch(body=request)
        return resp

    def get_by_matches(self, l):  # не готово
        body = {'multi_match': {}}
        for key in l.keys():
            for match in l[key]:
                if key in body['multi_match']:
                    body['multi_match'][key].append(match)
                else:
                    body['multi_match'][key] = [match]
        body_ = dict()
        body_['query'] = body
        print(body)
        res = self.es.search(body=body_)
        return res


elastic = ElasticLoader()
# print(elastic.search({'imports': ["python-telegram"], 'languages': ["c++", "python"], }))
# elastic.delete_index('github')
# elastic.create_index('data', 'github')
print(elastic.get_by_matches({"languages": ["cpp", "python"]}))
