import json
from elasticsearch import Elasticsearch
es = Elasticsearch(HOST="http://localhost", PORT=9200)
print(es.ping())
# es.indices.create(index="first_index")
print(es.indices.exists(index="first_index"))
'''doc_1 = {"city": "Paris", "country": "France"}
doc_2 = {"city": "Vienna", "country": "Austria"}
doc_3 = {"city": "London", "country": "England"}
'''


doc_1 = {"sentence": "Hack COVID-19"}
doc_2 = {"sentence": "Hack-Quarantine is stunning!"}
doc_3 = {"sentence": "Hackers are rich."}
es.index(index="english", doc_type="sentences", id='121', document=doc_1)
es.index(index="english", doc_type="sentences", id='221242', document=doc_2)
es.index(index="english", doc_type="sentences", id='36346', document=doc_3)

doc_1 = {"id": 1, "readme": "project for telegram", "tools": ["cpp", "c"]}
doc_2 = {"id": 2, "readme": "vkontakte bot for translating texts", "tools": ["python", "go"]}
doc_3 = {"id": 3, "readme": "Binary tree", "tools": ["java"]}
es.index(index="git", doc_type="sentences", document=doc_1)
es.index(index="git", doc_type="sentences", document=doc_2)
es.index(index="git", doc_type="sentences", document=doc_3)

body = {
    "from": 0,
    "size": 2,
    "query": {
        "match": {
            "tools": "cpp",
            "readme": "for"
        }
    }
}


def info(es):
    print("Ping:", es.ping())
    print("info:")
    s = es.info()
    # s = s.replace('\'', '"')
    print(s)


def m_search(d):  # {"languages": ["...", ...], "percentages": []}
    # search by multiple parameters: https://stackoverflow.com/questions/28546253/
    # how-to-create-request-body-for-python-elasticsearch-msearch/37187352
    search_arr = list()
    search_arr.append({'index': 'git'})
    search_arr.append({"query": {"match_phrase": {"readme": "for"}}, 'from': 0, 'size': 2})

    search_arr.append({'index': 'git'})
    search_arr.append({"query": {"match_phrase": {"tools": "cpp"}}, 'from': 0, 'size': 2})

    search_arr.append({'index': 'git'})
    search_arr.append({"query": {"match_phrase": {"tools": "python"}}, 'from': 0, 'size': 2})

    request = ''
    for each in search_arr:
        request += '%s \n' %json.dumps(each)

    # as you can see, you just need to feed the <body> parameter,
    # and don't need to specify the <index> and <doc_type> as usual
    resp = es.msearch(body=request)
    return resp


res = m_search()
print(res)
