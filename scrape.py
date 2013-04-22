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

#with open('raw_data.json', 'w') as f:
#    f.write(json.dumps(data))

with open('raw_data.json', 'r') as f:
    data = json.loads(f.read())

data_final = [{'day': dateutil.parser.parse(d['created_at']).toordinal()}
              for d in data
              if d['type'] == 'PushEvent']

data_final = {}
for d in data:
    year = dateutil.parser.parse(d['created_at']).year
    month = dateutil.parser.parse(d['created_at']).month
    key = (year, month)
    data_final[key] = data_final.get(key, 0) + 1

#data_final = [{'events': v, 'date':datetime.date(k[0],k[1],1).toordinal()} 
data_final = [{
    'events': v,
    'date':time.mktime(datetime.datetime(k[0],k[1],1).timetuple())*1000,
              }
              for (k, v) in data_final.items()]

#data_final.sort(lambda x,y: x['date'] < y['date'])
data_final.sort(key = lambda x: x['date'])

print(data_final)

json_data = json.dumps(data_final)

with open('data0.json', 'w') as f:
    f.write(json_data)
