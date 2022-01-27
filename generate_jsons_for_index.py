import GetJSON
import os

links = [
        'https://github.com/pallets/flask',
        'https://github.com/keras-team/keras',
        'https://github.com/scrapy/scrapy',
        'https://github.com/public-apis/public-apis'
    ]
if not os.path.exists('jsons'):
        os.mkdir('jsons')
for l in links:
    json = GetJSON.get_json(l, 1)
    name = l.split('/')[-1]
    name = name.strip('\n')
    data = GetJSON.get_json(l.strip(), True)
    with open('jsons/' + name + '.json', 'w') as file:
        file.write(data)


