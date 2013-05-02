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

    features = set([]).union(*[user.keys() for user in scraping_data])
    languages = [f for f in features if f[:5] == 'lang:' and not f == 'lang:None']
    reduced_array, top10 = top_feature_matrix(scraping_data, languages, 10)

    W, V = np.linalg.eig(np.cov(reduced_array.T))

    ordering = W.argsort()

    W0, W1 = W[ordering[-1]], W[ordering[-2]]
    V0, V1 = V[:, ordering[-1]], V[:, ordering[-2]]
    if abs(min(V0)) > max(V0):
        V0 *= -1
    if abs(min(V1)) > max(V1):
        V1 *= -1

    for i, (f, c) in enumerate(top10):
        print(round(V0[i],1), '\t', round(V1[i],1), '\t', f)

    #

    user_id = dict([(u['login'], i) for i, u in enumerate(scraping_data)])

    data_all = {'nodes': [], 'links': []}

    for i, user in enumerate(scraping_data):
        data_all['nodes'].append({'pc0': sum(V0 * reduced_array[i]),
                              'pc1': sum(V1 * reduced_array[i]),
                              'login': user['login'],
                              'url': user['url'],
                              'avatar_url': user.get('avatar_url', ''),
                              'id': i})


    key_events = set(['PullRequestEvent', 'PushEvent', 'IssueCommentEvent', 'IssuesEvent'])

    links = {}

    for i, user in enumerate(scraping_data):
        # build links
        counts = collections.Counter([event['repo']['name'].split('/')[0]
                                         for event in user['events']
                                         if event['type'] in key_events])
        counts.pop(user['login'], None)
        for collaborator, count in counts.iteritems():
            if collaborator in user_id:
                try:
                    pt0 = min(user['login'], collaborator)
                    pt1 = max(user['login'], collaborator)
                    links[(pt0, pt1)] = links.get((pt0, pt1), 0) + count
                except Exception as e:
                    # TODO: fix this!
                    pass
        data_all['nodes'][i]['total_collaboration'] = sum(counts.values())
        data_all['nodes'][i]['hs_collaboration'] = sum([v for k,v in counts.iteritems()
                                                       if k in user_id])

        data_all['links'] = [{'source': user_id[pt0], 'target': user_id[pt1], 'weight': weight}
                              for (pt0, pt1), weight in links.iteritems()]

    # output data

    json_data = json.dumps(data_all, indent=1)

    with open('website/data/hackers_pca.json', 'w') as f:
        f.write(json_data)
