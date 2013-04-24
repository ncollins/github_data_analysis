# Scrape data from api.github.com and output JSON data
# suitable for rendering with D3.js.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import json

with open('hackers.json', 'r') as f:
    data = json.loads(f.read())

data_graph = {
            'nodes': [],
            'links': [],
            }

position_dict = {}
for i, p in enumerate(data):
    login = p['login']
    position_dict[login] = i
    data_graph['nodes'].append({'name': login})

for p in data:
    i = position_dict[p['login']]
    for f in p['followers']:
        j = position_dict[f]
        data_graph['links'].append({'source': j, 'target': i})


json_data = json.dumps(data_graph)

with open('hackers_graph.json', 'w') as f:
    f.write(json_data)
