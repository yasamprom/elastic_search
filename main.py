import json
import os
from elasticsearch import Elasticsearch
from elasticsearch import exceptions as errors
from multipledispatch import dispatch

import warnings
warnings.filterwarnings("ignore")        # Разумеется, это временно


class ElasticLoader:
    """
        ElasticLoader provides functionality for creating an index and searching through it using the Elastic Search API
        By default, the index is called similar_projects, it is stored in the index_ value
    """

    # index_ = "similar_projects"

    def __init__(self, host="http://localhost", port=9200):
        """
            Connecting to the elastic search server using your own host and port
            By default, it is connected locally to http://localhost:9200
        """

        self.es = Elasticsearch(HOST=host, PORT=port)
        if not self.es.ping():
            print("Connection to " + host + ":" + str(port) + " failed")
            exit()

    def create_index(self, index, doc_type=None, ind=1, directory='.'):
        """
            Simply creates an index using json files

        :param index: the name of index
        :param doc_type: the doc_type of elements
        :param ind: the the number for indexing elements (first : ind, second : ind + 1, etc.)
        :param directory: path to json files (will use all files ended with .json, be careful)
        """
        cnt = 0
        try:
            self.es.indices.create(index=index)
            for file in os.listdir(directory):
                if file.endswith('.json'):
                    path = directory + '/' + file
                    doc = json.load(open(path))
                    if cnt == 0:
                        print(doc)
                        cnt = 1
                    self.add_by_json(d=doc, index=index, doc_type=doc_type, id_=ind)
                    ind += 1
        except errors.RequestError:
            print("Index " + index + " already exists")
            return

    @staticmethod
    def get_json(url):
        return {}

    def add_by_json(self, d, index, doc_type=None, id_=None):
        """
            Adds and element to the index using json (python dict) file

        :param d: python dict with description of element for index
        :param index: the name of index
        :param doc_type: the doc_type of elements
        :param id_: unique id for the element
        """

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

    def get(self):
        pass

    def delete_index(self, index):
        """
            Deletes the index

        :param index: the name of index
        """

        try:
            if input(("Delete " + index + " index? Y/n: ")) == "Y":
                self.es.indices.delete(index=index)
        except errors.NotFoundError:
            print("Index " + index + " does not exist")
            exit()

    def update_index(self, index, doc_type=None, ind=1, directory='.'):
        """
            Combination of delete and create functions

        :param index: the name of index
        :param doc_type: the doc_type of elements
        :param ind: the the number for indexing elements (first : ind, second : ind + 1, etc.)
        :param directory: path to json files (will use all files ended with .json, be careful)
        """

        self.delete_index(index=index)
        self.create_index(index=index, doc_type=doc_type, ind=ind, directory=directory)

    def search(self, d, index, limit=3):
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
        except errors.ElasticsearchException:
            print("Something is wrong with your query")
            exit()

    @dispatch(str, list, list)
    def get_by_multi_match(self, index, pairs_must: list, pairs_must_not: list):
        """
            Searching by list of pairs

        :param pairs_must: [field_1, value_1], ...] means field_i must be value_i
        :param pairs_must_not: [[field_1, value_1], ...] means filed_i must not be value_i
        :return: python dictionary of found elements
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
            # print(sub_dict)
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
            # print(sub_dict)
            body["query"]["bool"]["must_not"].append({
                'multi_match': sub_dict
                }
            )
        print(body)
        res = self.es.search(body=body)
        array = []

        for i in range(max(0, len(res['hits']['hits']))):
            array.append(res['hits']['hits'][i]['_source']['repo_name:'])
        return array


elastic = ElasticLoader()
index_name = 'test_index'
elastic.create_index(index=index_name, directory='./JSONs')
# list_must = [['languages', "python"], ['languages', 'shell'], ['languages', 'Makefile']]
# list_must_not = []
# print(elastic.get_by_multi_match(list_must, list_must_not))

# print("One match")
# qm1 = [['languages', 'python'], ['imports', 'monkeytype noneType']]
# qmn1 = []
# print(str(qm1))
# print(str(qmn1))
# print(elastic.get_by_multi_match(index_name, qm1, qmn1), '\n\n\n')


print("One match")
qm1 = [['languages', 'python']]
qmn1 = []
print(str(qm1))
print(str(qmn1))
print('\n'.join(elastic.get_by_multi_match(index_name, qm1, qmn1)), '\n\n\n')

print("Two matches")
qm2 = [['languages', 'python'], ['languages', 'shell']]
qmn2 = []
print(str(qm2))
print(str(qmn2))
print('\n'.join(elastic.get_by_multi_match(index_name, qm2, qmn2)), '\n\n\n')

print("Two matches with MUST_NOT var.")
qm4 = [['languages', 'python'], ['languages', 'shell']]
qmn4 = [['languages', 'Makefile']]
print(str(qm4))
print(str(qmn4))
print('\n'.join(elastic.get_by_multi_match(index_name, qm4, qmn4)), '\n\n\n')

print("Three matches with MUST_NOT var.")
qm4 = [['languages', 'python'], ['languages', 'shell'], ['languages', 'javascript']]
qmn4 = [['languages', 'Makefile']]
print(str(qm4))
print(str(qmn4))
print('\n'.join(elastic.get_by_multi_match(index_name, qm4, qmn4)), '\n\n\n')

print("MUST is equal MUST_NOT")
qm3 = [['languages', 'python'], ['languages', 'shell']]
qmn3 = [['languages', 'python'], ['languages', 'shell']]
print(str(qm3))
print(str(qmn3))
print('\n'.join(elastic.get_by_multi_match(index_name, qm3, qmn3)), '\n\n\n')

print("Three matches")
qm5 = [['languages', 'python'], ['languages', 'shell'], ['imports', 'requests']]
qmn5 = []
print(str(qm5))
print(str(qmn5))
print('\n'.join(elastic.get_by_multi_match(index_name, qm5, qmn5)), '\n\n\n')

print('Two matches, exact string')
qm5 = [['languages', 'python'], ['imports', 'cola functions counter CounterServer']]
qmn5 = []
print(str(qm5))
print(str(qmn5))
print('\n'.join(elastic.get_by_multi_match(index_name, qm5, qmn5)), '\n\n\n')

print('Two matches, not exact string')
qm5 = [['languages', 'python'], ['imports', 'cola CounterServer']]
qmn5 = []
print(str(qm5))
print(str(qmn5))
print('\n'.join(elastic.get_by_multi_match(index_name, qm5, qmn5)), '\n\n\n')

print('Three matches, not exact string')
qm5 = [['languages', 'python'], ['imports', 'monkeytype nonetype']]
qmn5 = []
print(str(qm5))
print(str(qmn5))
print('\n'.join(elastic.get_by_multi_match(index_name, qm5, qmn5)), '\n\n\n')

print('Three matches, not exact (bad) string')
qm5 = [['languages', 'python'], ['imports', 'monkeyType Nonetype']]
qmn5 = []
print(str(qm5))
print(str(qmn5))
print('\n'.join(elastic.get_by_multi_match(index_name, qm5, qmn5)), '\n\n\n')


print("Simple MUST and MUST_NOT")
qm1 = [['imports', 'base64']]
qmn1 = [['languages', 'shell']]
print(str(qm1))
print(str(qmn1))
print('\n'.join(elastic.get_by_multi_match(index_name, qm1, qmn1)), '\n\n\n')

print("query with dict")
q = {'query': {'bool': {'must': [{'multi_match': {'fields': ['imports'], 'query': 'base64', 'type': 'cross_fields', 'operator': 'AND'}}], 'must_not': [{'multi_match': {'fields': ['languages'], 'query': 'shell', 'type': 'cross_fields', 'operator': 'AND'}}]}}}
print(q)
print(elastic.get_by_multi_match(q))
