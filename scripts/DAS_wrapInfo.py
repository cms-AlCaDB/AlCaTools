#!/usr/bin/env python

import os
import re
import sys
import glob
import json
import math
import bisect
import random
import signal
import cPickle
import difflib
import argparse
import functools
import subprocess
import multiprocessing
import Utilities.General.cmssw_das_client as cmssw_das_client

################################################################################
def find_key(collection, key):
    """Searches for `key` in `collection` and returns first corresponding value.
    Arguments:
    - `collection`: list of dictionaries
    - `key`: key to be searched for
    """

    for item in collection:
        if key in item:
            return item[key]
    print(collection)
    raise KeyError(key)

################################################################################
def das_client(query, check_key = None):
    """
    Submit `query` to DAS client and handle possible errors.
    Further treatment of the output might be necessary.
    Arguments:
    - `query`: DAS query
    - `check_key`: optional key to be checked for; retriggers query if needed
    """

    error = True
    for i in xrange(5):         # maximum of 5 tries
        das_data = cmssw_das_client.get_data(query, limit = 0)

        if das_data["status"] == "ok":
            if das_data["nresults"] == 0 or check_key is None:
                error = False
                break

            result_count = 0
            for d in find_key(das_data["data"], check_key):
                result_count += len(d)
            if result_count == 0:
                das_data["status"] = "error"
                das_data["reason"] = ("DAS did not return required data.")
                continue
            else:
                error = False
                break

    if das_data["status"] == "error":
        print_msg("DAS query '{}' failed 5 times. \nThe last time for the the following reason:".format(query))
        print(das_data["reason"])
        sys.exit(1)
    return das_data["data"]

################################################################################
def get_datasets(dataset_pattern):
    """Retrieve list of dataset matching `dataset_pattern`.
    Arguments:
    - `dataset_pattern`: pattern of dataset names
    """

    data = das_client("dataset dataset={0:s} system=dbs3 | grep dataset.name"
                      .format(dataset_pattern), "dataset")
    return [find_key(f["dataset"], "name") for f in data]

################################################################################
def get_events_per_dataset(dataset_name):
    """Retrieve the number of a events in `dataset_name`.
    Arguments:
    - `dataset_name`: name of a dataset
    """

    return _get_events("dataset", dataset_name)

################################################################################
def get_size_per_dataset(dataset_name):
    """Retrieve the size of `dataset_name`.
    Arguments:
    - `dataset_name`: name of a dataset
    """

    return _get_size("dataset", dataset_name)

################################################################################
def get_events_per_file(file_name):
    """Retrieve the number of a events in `file_name`.
    Arguments:
    - `file_name`: name of a dataset file
    """

    return _get_events("file", file_name)

################################################################################
def _get_events(entity, name):
    """Retrieve the number of events from `entity` called `name`.
    Arguments:
    - `entity`: type of entity
    - `name`: name of entity
    """

    data = das_client("{0:s}={1:s} system=dbs3 | grep {0:s}.nevents"
                      .format(entity, name), entity)
    return int(find_key(find_key(data, entity), "nevents"))

################################################################################
def _get_size(entity, name):
    """Retrieve the number of events from `entity` called `name`.
    Arguments:
    - `entity`: type of entity
    - `name`: name of entity
    """

    data = das_client("{0:s}={1:s} system=dbs3 | grep {0:s}.size"
                      .format(entity, name), entity)
    return int(find_key(find_key(data, entity), "size"))

################################################################################
def print_msg(text, line_break = True, log_file = None):
    """Formatted printing of `text`.
    Arguments:
    - `text`: string to be printed
    """

    msg = "  >>> " + str(text)
    if line_break:
        print(msg)
    else:
        print(msg,sys.stdout.flush())
    if log_file:
        with open(log_file, "a") as f: f.write(msg+"\n")
    return msg


################################################################################
def main():

    dataset_name = "/*/*2016*SiStripCalMinBias*Prompt*/ALCARECO"
    datasets = get_datasets(dataset_name)
    
    pool = multiprocessing.Pool(
        10,     
        initializer = lambda: signal.signal(signal.SIGINT, signal.SIG_IGN))

    print_msg("Requesting information for the following dataset(s):")
    for d in datasets: 
        print_msg("\t"+d)
    print_msg("This may take a while...")

    result = pool.map_async(get_size_per_dataset,datasets).get(sys.maxint)    
    for count, elem in enumerate(result):
        print("==>",datasets[count],float(elem)/(1000*1000*1000),"GB")

    print("total=",float(sum(result))/(1000*1000*1000),"GB")


################################################################################
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
