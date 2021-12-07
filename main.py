import json
import os
from elasticsearch import Elasticsearch
from elasticsearch import exceptions as elasticerrors
from multipledispatch import dispatch


class ElasticLoader:
    index_ = "similar_projects"

    def __init__(self, host="http://localhost", port=9200):
        try:
            self.es = Elasticsearch(HOST=host, PORT=port)
        except RuntimeError:
            print("Connection failed")
            exit()

    def create_index(self, index=index_, doc_type=None, ind=1, directory='.'):
        try:
            self.es.indices.create(index=index)
            for file in os.listdir(directory):
                if file.endswith('.json'):
                    path = directory + '/' + file
                    doc = json.load(open(path))
                    self.add_by_json(d=doc, index=index, doc_type=doc_type, id_=ind)
                    ind += 1
        except elasticerrors.ElasticsearchException:
            print("Index already exists")
            return

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

    @dispatch(dict)
    def get_by_multi_match(self, d: dict) -> list:
        """
            Search by query as in elasticsearch
            Documentation: https://www.elastic.co/guide/en/elasticsearch/reference/current/search-your-data.html

            :param d: elastic_search-like python dictionary with query
            :param cnt: number of elements you want to get
            :return: python dictionary of found elements
        """
        try:
            res = self.es.search(body=d)
            array = []
            for i in range(len(res['hits']['hits'])):
                array.append(res['hits']['hits'][i]['_source'])
            return array
        except elasticerrors.ElasticsearchException:
            print("Something is wrong with your query")
            exit()

    @dispatch(list, list)
    def get_by_multi_match(self, pairs_must: list, pairs_must_not: list):
        """
            Searching by list of pairs must: [[field_1, value_1], ...]
                                    must_not: [[field_1, value_1], ...]
        """
        # d: line for search
        # op: {"AND", "OR"} (match in fields intersection or no)
        if pairs_must is None:
            raise ValueError('empty query')

        body = {
            "query": {
                "bool": {
                    "must": [],
                    "must_not": []
                }
            }
        }
        for p in pairs_must:
            sub_dict = {'fields': [p[0]],
                        'query': p[1],
                        "type": "cross_fields",
                        "operator": "AND"
                        }
            print(sub_dict)
            body["query"]["bool"]["must"].append({
                'multi_match': sub_dict
                }
            )
        for p in pairs_must_not:
            sub_dict = {'fields': [p[0]],
                        'query': p[1],
                        "type": "cross_fields",
                        "operator": "AND"
                        }
            print(sub_dict)
            body["query"]["bool"]["must_not"].append({
                'multi_match': sub_dict
                }
            )
        # bool : should : match languages : "....", match imports : "....", ...
        print(body)
        res = self.es.search(body=body)
        array = []
        print(max(0, len(res['hits']['hits'])))
        for i in range(max(0, len(res['hits']['hits']))):
            array.append(res['hits']['hits'][i]['_source'])
        return array


elastic = ElasticLoader()
# elastic.create_index()
list_must = [['languages', "python"], ["imports", "MRjob"]]
list_must_not = []

print(elastic.get_by_multi_match(list_must, list_must_not))
# must
#    lang : ....
#    imports : ...
# must_not:
#   langs : ....
#   imports: ....
