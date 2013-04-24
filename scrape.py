# Scrape data from api.github.com and output JSON data
# suitable for rendering with D3.js.

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import urllib2
import json
import dateutil
import datetime
import time

import requests

import login
import hacker_school

user_url = 'https://api.github.com/users/{}'

def setup_auth(domain, username, password):
    # create a password manager
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    # Add the username and password.
    # If we knew the realm, we could use it instead of None.
    password_mgr.add_password(None,
                              'https://api.github.com',
                              login.username,
                              login.password)
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    # create "opener" (OpenerDirector instance)
    opener = urllib2.build_opener(handler)
    # Install the opener.
    # Now all calls to urllib2.urlopen use our opener.
    urllib2.install_opener(opener)


def get_page(url):
    try:
        r = requests.get(url, auth=(login.username, login.password))
        return r.json()
        #return json.loads(urllib2.urlopen(url).read())
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
    setup_auth('api.github.com', login.username, login.password)

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
