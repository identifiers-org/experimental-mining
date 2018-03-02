# This script provides some reporting on the resolver data from identifiers.org
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
metadata_service_endpoint_from_url = "http://metadata.api.aws.identifiers.org/getMetadataForUrl"

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


def get_metadata_for_url(url):
    """
    This Helper queries the metadata service with a URL, 
    and returns its response back to the caller for further interpretation
    """
    n_attempts = 42
    response = None
    while n_attempts:
        n_attempts -= 1
        try:
            response = requests.post(metadata_service_endpoint_from_url, json={"url": url})
        except Exception as e:
            # Any possible exception counts towards the attempt counter
            # Random wait - TODO - Another magic number!!!
            time.sleep(random.randint(3))
            continue
        if response.ok:
            print("[METADATA][OK] - '{}'".format(url))
            break
        else:
            print("[METADATA][ERROR] - '{}'".format(url))
            break
        # Random wait - TODO - Another magic number!!!
    return response


# Get the resolver data
resolver_dump = make_rest_request_content_type_json(identifiersorg_resolver_data_url)

# Workout how many prefixes there are in identifiers.org
# prefixes = set([pid_entry['prefix'] for pid_entry in resolver_dump])
# print("There are #{} Compact ID prefixes registered in identifiers.org".format(len(prefixes)))

# Check the distribution of resources
#resource_prefixes = []
#for pid_entry in resolver_dump:
#    if 'resources' in pid_entry:
#        for resource in pid_entry['resources']:
#            if 'resourcePrefix' in resource:
#                resource_prefixes.append(resource['resourcePrefix'])
#            else:
#                print("NO RESOURCE PREFIX FOR: PID Entry Name '{}', Resource Information '{}'".format(pid_entry['name'], resource['info']))

# resource_prefixes_distribution = Counter(resource_prefixes)
# print("There #{} Resource Selectors in identifiers.org".format(len(resource_prefixes_distribution.keys())))

# Plotting the distribution
#labels = sorted(resource_prefixes_distribution.keys())
#values = [resource_prefixes_distribution.get(key) for key in labels]
# I don't like this Pie Chart
#fig1, ax1 = plt.subplots()
#fig1.set_size_inches(18, 5)
#ax1.bar(labels, values, 1/1.5, color="blue")
#ax1.pie(values, labels=labels, shadow=True, startangle=90)
#ax1.axis('equal')
#plt.show()


# Create a report on metadata
columns = ['PidEntryName',
           'PidEntryPrefix',
           'PidEntryUrl', 
           'ResourceInfo', 
           'ResourceInstitution', 
           'ResourceLocation', 
           'ResourceOfficial', 
           'ResourcePrefix', 
           'ResourceLocalId', 
           'WasMetadataFound', 
           'MetadataContent', 
           'ResourceTestUrl', 
           'MetadataServiceResponseStatus', 
           'MetadataServiceResponseError',
           'HomeUrl',
           'HomeUrlWasMetadataFound',
           'HomeUrlMetadataContent',
           'HomeUrlMetadataServiceResponseStatus',
           'HomeUrlMetadataServiceResponseError']
metadata_report = pandas.DataFrame(columns=columns)

# Prepare the URLs and initial report (I could have done everything in one pass,
# but this is just investigating the dataset)
for pid_entry in resolver_dump:
    entry = pandas.Series(['---'] * len(columns), index=columns)
    entry.PidEntryName = pid_entry['name']
    entry.PidEntryPrefix = pid_entry['prefix']
    entry.PidEntryUrl = pid_entry['url']
    if ('resources' not in pid_entry) or (not pid_entry['resources']):
        metadata_report = metadata_report.append(entry, ignore_index=True)
    for resource in pid_entry['resources']:
        resource_entry = entry.copy()
        resource_entry.ResourceInfo = resource['info']
        resource_entry.ResourceInstitution = resource.get('institution', '---')
        resource_entry.ResourceLocation = resource.get('location', '---')
        resource_entry.ResourceOfficial = resource.get('official', '---')
        resource_entry.ResourcePrefix = resource.get('resourcePrefix', '---')
        resource_entry.ResourceLocalId = resource.get('localId', '---')
        resource_entry.WasMetadataFound = 'No'
        resource_entry.ResourceTestUrl = None
        if ('accessURL' in resource) and ('localId' in resource):
            resource_entry.ResourceTestUrl = resource['accessURL'].replace('{$id}', resource['localId'])
        # Fill in the information for the home URL
        if 'resourceURL' in resource:
            resource_entry.HomeUrl = resource['resourceURL']
        resource_entry.HomeUrlWasMetadataFound = 'No'
        metadata_report = metadata_report.append(resource_entry, ignore_index=True)

# Print out information on the test URLs
print("Test URLs description\n{}".format(metadata_report.ResourceTestUrl.describe()))
print("Sample content\n{}".format(metadata_report.head()))

# Build the report
# Parallel call to metadata service, this is a lot slower, good enough as proof of concept
#metadata_requests = {index: threading.Thread(target=get_metadata_for_url(metadata_report.loc[index].ResourceTestUrl)) for index in range(metadata_report.shape[0]) if metadata_report.loc[index].ResourceTestUrl}
# Parallel wrapper - Version using multiprocessing, it crashes within Jupyter
#def metadata_request_parallel_wrapper(context, url):
#    context.put(get_metadata_for_url(url))
#metadata_requests = {index: multiprocessing.Process(target=metadata_request_parallel_wrapper, args=(multiprocessing.Queue(), metadata_report.loc[index].ResourceTestUrl),) for index in range(metadata_report.shape[0]) if metadata_report.loc[index].ResourceTestUrl}
#metadata_requests = {index: multiprocessing.Process(target=get_metadata_for_url, args=(metadata_report.loc[index].ResourceTestUrl,)) for index in range(metadata_report.shape[0]) if metadata_report.loc[index].ResourceTestUrl}
#[process.start() for process in metadata_requests.values()]

# Another approach, with Thread Pool
pool = Pool(processes=mp.cpu_count())

print("{} COLLECTING METADATA FOR COMPACT ID LANDING PAGE {}".format("=" * 12, "=" * 12))
# Get metadata for ComapactId landing page
indexes_to_process = [index for index in range(metadata_report.shape[0]) if metadata_report.loc[index].ResourceTestUrl]
metadata_requests = pool.map(get_metadata_for_url, metadata_report.ResourceTestUrl[indexes_to_process])
for (index, response) in zip(indexes_to_process, metadata_requests):
    if response.ok:
        metadata_report.loc[index].WasMetadataFound = 'Yes'
        metadata_report.loc[index].MetadataContent = response.json()['metadata']
        print("[METADATA][OK] - '{}'".format(metadata_report.loc[index].ResourceTestUrl))
    else:
        print("[METADATA][ERROR] - '{}'".format(metadata_report.loc[index].ResourceTestUrl))
    if 'errorMessage' in response.json():
        metadata_report.loc[index].MetadataServiceResponseError = response.json()['errorMessage']
    else:
        metadata_report.loc[index].MetadataServiceResponseError = "METADATA SERVICE ERROR"
        print("[METADATA][QUERY_ERROR] - '{}', response '{}'".format(metadata_report.loc[index].ResourceTestUrl, response.json()))
    metadata_report.loc[index].MetadataServiceResponseStatus = response.status_code
print("=" * 48)

print("{} COLLECTING METADATA FOR RESOURCE URL {}".format("=" * 12, "=" * 12))
# Get metadata for Home URLs (Resource URLs) landing page
indexes_to_process = [index for index in range(metadata_report.shape[0]) if metadata_report.loc[index].HomeUrl]
metadata_requests = pool.map(get_metadata_for_url, metadata_report.HomeUrl[indexes_to_process])
for (index, response) in zip(indexes_to_process, metadata_requests):
    if response.ok:
        metadata_report.loc[index].HomeUrlWasMetadataFound = 'Yes'
        metadata_report.loc[index].HomeUrlMetadataContent = response.json()['metadata']
        print("[METADATA][OK] - '{}'".format(metadata_report.loc[index].HomeUrl))
    else:
        print("[METADATA][ERROR] - '{}'".format(metadata_report.loc[index].HomeUrl))
    if 'errorMessage' in response.json():
        metadata_report.loc[index].HomeUrlMetadataServiceResponseError = response.json()['errorMessage']
    else:
        metadata_report.loc[index].HomeUrlMetadataServiceResponseError = "METADATA SERVICE ERROR"
        print("[METADATA][QUERY_ERROR] - '{}', response '{}'".format(metadata_report.loc[index].HomeUrl, response.json()))
    metadata_report.loc[index].HomeUrlMetadataServiceResponseStatus = response.status_code
print("=" * 48)

# Have another look at the metadata table
print("After collecting metadata, the report looks like\n{}".format(metadata_report.head()))
# Dump report to file
metadata_report.to_csv('metadata_detailed_report.csv', encoding='utf-8')
