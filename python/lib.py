#!/usr/bin/python
# a library of useful functions
import os
import json
import subprocess
import time

dir = os.path.dirname(__file__) # get absolute file path
data_dir = os.path.join(dir, '../data/')
shell_dir = os.path.join(dir, '../shell/')

def fetch_api( args ):
    "executes the shell script getJson.sh to fetch data from the lol api"
    shellfile = os.path.abspath( os.path.join( shell_dir, 'getJson.sh' ) )
    subprocess.call([shellfile] + args)
    time.sleep(1)
    return

def json_dump( file_name, json_data, path=None ):
    "dumps a json data structure to a file as a json string"
    if path == None:
        json_file = os.path.abspath( os.path.join( data_dir, file_name ) )
    else:
        json_file = os.path.abspath( os.path.join( dir, path + file_name ) )

    with open(json_file, 'w') as _file:
        json.dump(json_data, _file)
    print "updated file " + json_file
    return

def json_load( file_name, path=None ):
    "loads the json string from a file and returns a json data structure"
    if path == None:
        json_file = os.path.abspath( os.path.join( data_dir, file_name ) )
    else:
        json_file = os.path.abspath( os.path.join( dir, path + file_name ) )

    with open(json_file) as _file:
        json_data = json.load(_file)
    return json_data
