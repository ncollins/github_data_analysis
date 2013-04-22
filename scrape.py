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

import login

url = 'https://api.github.com/users/ncollins/events?page={}'

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

# use the opener to fetch a URL
opener.open(a_url)

# Install the opener.
# Now all calls to urllib2.urlopen use our opener.
urllib2.install_opener(opener)


def get_data(url, max_pages):
    data = []
    for i in range(max_pages):
        new_data = json.loads(urllib2.urlopen(url.format(i)).read())
        if new_data == []:
            break
        else:
            data.extend(new_data)
    return data

#data = get_data(url, 20)

with open('raw_data.json', 'w') as f:
    f.write(json.dumps(data))
