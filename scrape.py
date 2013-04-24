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


if __name__ == '__main__':
    data = []
    for person in hacker_school.people:
        user_page = get_page(user_url.format(person))
        d = {}
        d['login'] = person

        # followers
        followers_url = user_page['followers_url'] + '?page={}'
        followers_json, _ = get_pages(followers_url)
        followers = []
        for follower in followers_json:
            if follower['login'] in hacker_school.people:
                followers.append(follower['login'])
        d['followers'] = followers
        d['hs_followers_count'] = len(followers)

        # repos
        repos_url = user_page['repos_url'] + '?page={}'
        repos_json, _ = get_pages(repos_url)
        for repo in repos_json:
            #print(repo)
            size = repo['size']
            language = str(repo['language'])
            fork = repo['fork']
            forks = repo['forks']
            if fork == True:
                d['total_forks'] = d.get('total_forks', 0) + 1
            else:
                d['own_repo_size'] = d.get('own_repo_size', 0) + size
                d['lang:'+language] = d.get('lang:'+language, 0) + 1
                d['own_repo_count'] = d.get('own_repo_count', 0) + 1

        # add to main json data
        data.append(d)

    with open('hackers.json', 'w') as f:
        f.write(json.dumps(data))
