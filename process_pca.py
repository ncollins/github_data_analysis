# Scrape data from api.github.com and output JSON data
# suitable for rendering with D3.js.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import json
import collections
import numpy as np

import hacker_school


def top_feature_matrix(json_data, features, max_features = None):
    """
    Returns a NumPy matrix where the row index matches the original list
    and a list of the features (columns).
    """
    if max_features == None:
        max_features = len(features)

    full_array = np.ndarray((len(json_data), len(features)))

    for row, dat in enumerate(json_data):
        for col, feat in enumerate(features):
            full_array[row, col] = dat.get(feat, 0)

    top = sorted([(l, c) for l, c in zip(features, np.sum(full_array, 0))],
                   reverse = True,
                   key = lambda pair: pair[1])[:max_features]

    reduced_array = np.ndarray((len(json_data), max_features))

    for row, dat in enumerate(json_data):
        all_repos = dat.get('own_repo_count', 1)
        for col, (feat, _) in enumerate(top):
            reduced_array[row, col] = dat.get(feat, 0) #/ all_repos
        # other langs
        #reduced_array[row, 10] = all_repos - sum(reduced_array[row, :max_features])
        #reduced_array[row] = reduced_array[row] - all_repos/max_features

    reduced_array = reduced_array - np.average(reduced_array, 0)

    return reduced_array, top
    

if __name__ == '__main__':

    with open('website/data/hackers.json', 'r') as f:
        scraping_data = json.loads(f.read())

    features = set()
    for person in scraping_data:
        features.update(person.keys())
    features.difference_update(['events', 'followers', 'login', 'url', 'repos', 'avatar_url'])
    orderedfeatures = list(features)

    #full_array = np.ndarray((len(data_scraping), len(features)))

    #for row, p in enumerate(scraping_data):
    #    for col, f in enumerate(orderedfeatures):
    #        full_array[row, col] = p.get(f, 0)

    #top10 = sorted([(l, int(c)) for l, c in zip(orderedfeatures, np.sum(full_array, 0))
    #                if l[:5] == 'lang:' and not l == 'lang:None'],
    #               reverse = True,
    #               key = lambda pair: pair[1])[:10]

    #reduced_array = np.ndarray((len(scraping_data), 10+1))
    #for row, p in enumerate(scraping_data):
    #    all_repos = p.get('own_repo_count', 1)
    #    for col, (f, c) in enumerate(top10):
    #        reduced_array[row, col] = p.get(f, 0) #/ all_repos
    #    # other langs
    #    reduced_array[row, 10] = all_repos - sum(reduced_array[row, :10])
    #    reduced_array[row] = reduced_array[row] - all_repos/11

    #reduced_array = reduced_array - np.average(reduced_array, 0)

    languages = [f for f in features if f[:5] == 'lang:' and not f == 'lang:None']
    reduced_array, top10 = top_feature_matrix(scraping_data, languages, 10)

    w, v = np.linalg.eig(np.cov(reduced_array.T))

    ordering = w.argsort()

    w0, w1 = w[ordering[-1]], w[ordering[-2]]
    v0, v1 = v[ordering[-1]], v[ordering[-2]]

    for i, (f, c) in enumerate(top10):
        print(round(v0[i],1), '\t', round(v1[i],1), '\t', f)

    people = dict([(p['login'], p) for p in scraping_data])
    people_set = set(people.keys())
    people_numbers = dict([(p['login'], i) for i, p in enumerate(scraping_data)])

    data_nodes = []
    for i, p in enumerate(scraping_data):
        x = sum(v0 * reduced_array[i])
        y = sum(v1 * reduced_array[i])
        login = p['login']
        url = p['url']
        avatar_url = p.get('avatar_url', '')
        data_nodes.append({'x': x, 'y': y, 'login': login, 'url': url,
                           'avatar_url': avatar_url, 'id': people_numbers[login]})

    data_all = {'nodes': data_nodes, 'links': []}

    key_events = set(['PullRequestEvent', 'PushEvent', 'IssueCommentEvent', 'IssuesEvent'])

    people = dict([(p['login'], p) for p in data_nodes])
    people_set = set(people.keys())

    for person in scraping_data:
        #
        count = collections.Counter([event['repo']['name'].split('/')[0]
                             for event in person['events']
                             if event['type'] in key_events])
        #collaborators = set([k for k,v in count.items() if v > 1])
        collaborators = set([k for k,v in count.items() if v > 0])
        collaborators.difference_update([person['login']])
        collaborators.intersection_update(people_set)
        for c in collaborators:
            try:
                link = {'x1': people[person['login']]['x'],
                        'y1': people[person['login']]['y'],
                        'x2': people[c]['x'],
                        'y2': people[c]['y'],
                        'source': people_numbers[person['login']],
                        'target': people_numbers[c],
                       }
                data_all['links'].append(link)
            except Exception as e:
                print(e)
                # TODO: fix this!
                pass

    json_data = json.dumps(data_all, indent=1)

    with open('website/data/hackers_pca.json', 'w') as f:
        f.write(json_data)
