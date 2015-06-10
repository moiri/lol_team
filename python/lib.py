#!/usr/bin/python
# a library of useful functions
import os
import json

dir = os.path.dirname(__file__) # get absolute file path
data_dir = os.path.join(dir, '../data/')
private_dir = os.path.join(dir, '../server/private/')
myTeamId = "TEAM-106e2ea0-959c-11e3-a2ca-782bcb497d6f"
myTeamFileName = "team.json"
summonersFileName = "summoners.json"
championsFileName = "champions.json"

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
