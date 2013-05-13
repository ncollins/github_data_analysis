# Scrape data from api.github.com and output JSON data
# suitable for rendering with D3.js.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import json
import requests

import login
import hacker_school

from collections import defaultdict

user_url = 'https://api.github.com/users/{}'

def get_page(url):
    try:
        r = requests.get(url, auth=(login.username, login.password))
        return r.json()
    except Exception as e:
        print('Error getting: {}'.format(url))
        return None


def get_pages(url, max_pages=100):
    data = []
    for i in range(max_pages):
        print('GET: {}'.format(url.format(i)))
        new_data = get_page(url.format(i))
        data.extend(new_data)
        if len(new_data) < 30:
            break
    return data, i


def scrape_group(group):

    data = []
    for person in group:

        if person == 'hackerschool':
            user_page = get_page('https://api.github.com/orgs/hackerschool')
        else:
            user_page = get_page(user_url.format(person))

        # followers
        if user_page['followers'] > 0:
            followers_url = user_page['followers_url'] + '?page={}'
            followers_json, _ = get_pages(followers_url)

        else:
            followers_json = []

        # This should check all hacker schoolers, not just ones in the given group.
        followers = [follower for follower in followers_json if follower['login'] in group] 

        # repos
        repos_url = user_page['repos_url'] + '?page={}'
        repos_json, _ = get_pages(repos_url)

        total_forks = 0
        own_repo_size = 0
        own_repo_count = 0
        langs = defaultdict(int)

        for repo in repos_json:
            language = str(repo['language'])
            if repo['fork'] == True:
                total_forks += 1
            else:
                own_repo_size += repo['size']
                own_repo_count += 1
                langs[language] += 1

        # events
        events_url = user_page['events_url'].replace('{/privacy}','') + '?page={}'
        events_json, _ = get_pages(events_url)

        d = {
            'login': person,
            'url': user_page['html_url'],
            'avatar_url': user_page.get('avatar_url', ''),
            'followers': followers,
            'hs_followers_count': len(followers),
            'repos': repos_json,
            'events': events_json,
            'total_forks': total_forks,
            'own_repo_size': own_repo_size,
            'own_repo_count': own_repo_count
            }

        for language in langs.keys():
            d["lang:"+language] = langs[language]

        data.append(d)

    return data



if __name__ == '__main__':
    group = hacker_school.groups['winter2013']
    data = scrape_group(group)

    with open('data/hackers.json', 'w') as f:
        f.write(json.dumps(data, indent=1))
