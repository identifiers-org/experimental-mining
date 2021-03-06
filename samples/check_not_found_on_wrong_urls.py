# This script uses Resolver data for generating a list of URLs that should lead to error pages
#
# Author: Manuel Bernal Llinares <mbdebian@gmail.com>

import sys
import time
import random
import urllib3
import requests
import itertools
import threading
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
from threading import Thread
from collections import Counter
from multiprocessing import Pool, Process
from multiprocessing.pool import ThreadPool

# Endpoint from where the information is coming
identifiersorg_resolver_data_url = "https://identifiers.org/rest/collections/expand"

# Initialize pseudo-random number generator
random.seed(time.time())

# Disable warnings, hopefully for HTTPS connections
urllib3.disable_warnings()


# Helpers
def make_rest_request_content_type_json(url):
    # TODO - Magic number here!!!
    n_attempts = 42
    response = None
    while n_attempts:
        n_attempts -= 1
        try:
            response = requests.get(url, headers={"Content-Type": "application/json"}, timeout=3.0)
        except Exception as e:
            # Any possible exception counts towards the attempt counter
            # Random wait - TODO - Another magic number!!!
            time.sleep(random.randint(30))
            continue
        if response.ok:
            return response.json()
        # Random wait - TODO - Another magic number!!!
        time.sleep(random.randint(10))
    response.raise_for_status()


def chunks(mylist, chunksize):
    for i in range(0, len(mylist), chunksize):
        yield mylist[i: i + chunksize]


def check_url_http_status(url):
    http = urllib3.PoolManager()
    response = None
    counter = 3
    while counter > 0:
        try:
            response = http.request('GET', url, timeout=1.0)
            #if response.status == 200:
                #print("[  WRONG({})  ] {}".format(response.status, url))
                #pass
            #else:
                #print("[   OK({})    ] {}".format(response.status, url))
                #pass
            break
        except:
            time.sleep(1)
        counter -= 1
        if counter == 0:
            #print("[-RETRY__ERROR-] {}".format(url))
            pass
    if response:
        response = response.status
    return {"url": url, "response": response}


# Get the resolver data
resolver_dump = make_rest_request_content_type_json(identifiersorg_resolver_data_url)

print("---> Building URLs")
urls = []
for pid_entry in resolver_dump:
    if ('resources' not in pid_entry) or (not pid_entry['resources']):
        continue
    for resource in pid_entry['resources']:
        if ('accessURL' in resource) and ('localId' in resource):
            urls.append(str(resource['accessURL'].replace('{$id}', "TOTALLYWRONGIDFORSURE")))

print("---> Checking #{} URLs".format(len(urls)))
sys.stdout.flush()
# Check the URLS
nprocesses = mp.cpu_count() * 2
pool = Pool(processes=nprocesses)
responses = []
for i in range(0, len(urls), nprocesses):
    start = i
    end = i + nprocesses
    print("---> Exploring from {} to {}, out of {}".format(start, end - 1, len(urls)))
    sys.stdout.flush()
    batch = pool.map(check_url_http_status, urls[start : end])
    responses.extend(batch)
#responses = [check_url_http_status(url) for url in urls]
print("---> END, with #{} responses".format(len(responses)))
print("=" * 20 + " URL STATUS REPORT " + "=" * 20)
for response in responses:
    if not response["response"]:
        print("[---- ERROR ---] {}".format(response["url"]))
    elif response["response"] == 200:
        print("[  WRONG({})  ] {}".format(response["response"], response["url"]))
    else:
        print("[   OK({})    ] {}".format(response["response"], response["url"]))
