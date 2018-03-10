# This script uses Resolver data for generating a list of URLs that should lead to error pages
#
# Author: Manuel Bernal Llinares <mbdebian@gmail.com>

import sys
import time
import random
import pandas
import requests
import threading
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
from collections import Counter
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

# Endpoint from where the information is coming
identifiersorg_resolver_data_url = "https://identifiers.org/rest/collections/expand"

# Initialize pseudo-random number generator
random.seed(time.time())

# Helpers
def make_rest_request_content_type_json(url):
    # TODO - Magic number here!!!
    n_attempts = 42
    response = None
    while n_attempts:
        n_attempts -= 1
        try:
            response = requests.get(url, headers={"Content-Type": "application/json"})
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


# Get the resolver data
resolver_dump = make_rest_request_content_type_json(identifiersorg_resolver_data_url)

for pid_entry in resolver_dump:
    if ('resources' not in pid_entry) or (not pid_entry['resources']):
        continue
    for resource in pid_entry['resources']:
        if ('accessURL' in resource) and ('localId' in resource):
            print(str(resource['accessURL'].replace('{$id}', "TOTALLYWRONGIDFORSURE")))
