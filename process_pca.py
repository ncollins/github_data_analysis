# Scrape data from api.github.com and output JSON data
# suitable for rendering with D3.js.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import json
import numpy as np

with open('hackers.json', 'r') as f:
    data = json.loads(f.read())

features = set()
for person in data:
    features.update(person.keys())
features.difference_update(['followers', 'login'])
orderedfeatures = list(features)

full_array = np.ndarray((len(data), len(features)))

for row, p in enumerate(data):
    for col, f in enumerate(orderedfeatures):
        full_array[row, col] = p.get(f, 0)

top10 = sorted([(l, int(c)) for l, c in zip(orderedfeatures, np.sum(full_array, 0))
                if l[:5] == 'lang:' and not l == 'lang:None'],
               reverse = True,
               key = lambda pair: pair[1])[:10]

reduced_array = np.ndarray((len(data), 10))
for row, p in enumerate(data):
    for col, (f, c) in enumerate(top10):
        reduced_array[row, col] = p.get(f, 0) / p.get('own_repo_count', 1)

w, v = np.linalg.eig(np.cov(reduced_array.T))
#w, v = np.linalg.eig(np.corrcoef(reduced_array.T))

ordering = w.argsort()

w0, w1 = w[ordering[-1]], w[ordering[-2]]
v0, v1 = v[ordering[-1]], v[ordering[-2]]

#position_dict = {}
#for i, p in enumerate(data):
#    login = p['login']
#    position_dict[login] = i
#    data_graph['nodes'].append({'name': login})

#for p in data:
#    i = position_dict[p['login']]
#    for f in p['followers']:
#        j = position_dict[f]
#        data_graph['links'].append({'source': j, 'target': i})


#json_data = json.dumps(data_graph)

#with open('hackers_graph.json', 'w') as f:
#    f.write(json_data)
