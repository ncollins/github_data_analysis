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


def get_pages(url, max_pages):
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
        followers_url = user_page['followers_url']
        followers_page, pagecount = get_pages(followers_url+'?page={}', 20)
        followers = []
        for f in followers_page:
            if f['login'] in hacker_school.people:
                followers.append(f['login'])
        d['followers'] = followers
        data.append(d)

    with open('hackers.json', 'w') as f:
        f.write(json.dumps(data))
