# Scrape data from api.github.com and output JSON data
# suitable for rendering with D3.js.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import json
import numpy as np

import hacker_school

with open('data/hackers.json', 'r') as f:
    data = json.loads(f.read())

features = set()
for person in data:
    features.update(person.keys())
features.difference_update(['events', 'followers', 'login', 'url', 'repos'])
orderedfeatures = list(features)

full_array = np.ndarray((len(data), len(features)))

for row, p in enumerate(data):
    for col, f in enumerate(orderedfeatures):
        full_array[row, col] = p.get(f, 0)

top10 = sorted([(l, int(c)) for l, c in zip(orderedfeatures, np.sum(full_array, 0))
                if l[:5] == 'lang:' and not l == 'lang:None'],
               reverse = True,
               key = lambda pair: pair[1])[:10]

#top10avg = [(l, c/len(data)) for l,c in top10]

reduced_array = np.ndarray((len(data), 10+1))
for row, p in enumerate(data):
    all_repos = p.get('own_repo_count', 1)
    for col, (f, c) in enumerate(top10):
        reduced_array[row, col] = p.get(f, 0) #/ all_repos
    # other langs
    reduced_array[row, 10] = all_repos - sum(reduced_array[row, :10])
    reduced_array[row] = reduced_array[row] - all_repos/11

reduced_array = reduced_array - np.average(reduced_array, 0)

w, v = np.linalg.eig(np.cov(reduced_array.T))
#w, v = np.linalg.eig(np.corrcoef(reduced_array.T))

ordering = w.argsort()

w0, w1 = w[ordering[-1]], w[ordering[-2]]
v0, v1 = v[ordering[-1]], v[ordering[-2]]

for i, (f, c) in enumerate(top10):
    print(round(v0[i],1), '\t', round(v1[i],1), '\t', f)

data_nodes = []
for i, p in enumerate(data):
    x = sum(v0 * reduced_array[i])
    y = sum(v1 * reduced_array[i])
    login = p['login']
    url = p['url']
    data_nodes.append({'x': x, 'y': y, 'login': login, 'url': url})

data_all = {'nodes': data_nodes, 'links': []}

#for p1, p2 in zip(data_nodes[:-1], data_nodes[1:]):
#    data_all['links'].append({'x1': p1['x'],
#                              'y1': p1['y'],
#                              'x2': p2['x'],
#                              'y2': p2['y']})

people = dict([(p['login'], p) for p in data_nodes])
people_set = set(people.keys())

key_events = set(['PullRequestEvent', 'PushEvent', 'IssueCommentEvent', 'IssuesEvent'])

for person in data:
    collaborators = set([event['repo']['name'].split('/')[0]
                         for event in person['events']
                         if event['type'] in key_events])
    collaborators.difference_update([person['login']])
    collaborators.intersection_update(people_set)
    for c in collaborators:
        try:
            link = {'x1': people[person['login']]['x'],
                    'y1': people[person['login']]['y'],
                    'x2': people[c]['x'],
                    'y2': people[c]['y'],
                   }
            data_all['links'].append(link)
        except:
            # TODO: fix this!
            pass


json_data = json.dumps(data_all)

with open('data/hackers_pca.json', 'w') as f:
    f.write(json_data)
