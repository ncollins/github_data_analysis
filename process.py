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

with open('raw_data.json', 'r') as f:
    data = json.loads(f.read())

data_final = {}
for d in data:
    year = dateutil.parser.parse(d['created_at']).year
    month = dateutil.parser.parse(d['created_at']).month
    key = (year, month)
    data_final[key] = data_final.get(key, 0) + 1

data_final = [{
    'events': v,
    'date':time.mktime(datetime.datetime(k[0],k[1],1).timetuple())*1000,
              }
              for (k, v) in data_final.items()]

data_final.sort(key = lambda x: x['date'])

json_data = json.dumps(data_final)

with open('data0.json', 'w') as f:
    f.write(json_data)
