#!/usr/bin/python
# this script uses a match.json file and extracts parts of the keys to generate
# a database structure.

import MySQLdb
import lib

def genQueryAlterTable(table_name, json_data, primary=None):
    "function to add columns to a table"
    query = "ALTER TABLE " + table_name
    for key in json_data:
        if type(json_data[key]) is int:
            query += " ADD " + key + " INT(15) UNSIGNED"
            if key == primary:
                query += " PRIMARY KEY"
            query += ","
        elif type(json_data[key]) is str or type(json_data[key]) is unicode:
            query += " ADD " + key + " VARCHAR(50),"
        elif type(json_data[key]) is bool:
            query += " ADD " + key + " TINYINT(1) UNSIGNED,"
    query = query[:-1]
    query += ";"
    return query

# if set to true, teh script will only print the queries to the standard output
# but not execute them on the db
debug = False
# debug = True

# load database cretentials
db_creds = lib.json_load('db.json', '../private/')
user_lvl = 2 # all privileges

# load match data
match = lib.json_load('2117389806_match.json')

# Open database connection
db = MySQLdb.connect(
    db_creds['host'],
    db_creds['users'][user_lvl]['name'],
    db_creds['users'][user_lvl]['password'],
    db_creds['name']
)

# prepare a cursor object using cursor() method
cursor = db.cursor()

# create games table
query = "CREATE TABLE IF NOT EXISTS games (" + \
        "win TINYINT(1) UNSIGNED," + \
        "opposingTeamName VARCHAR(50));"
if debug: print query
else: cursor.execute(query)

# add columns to games table
query = genQueryAlterTable('games', match, 'matchId')
if debug: print query
else: cursor.execute(query)

# create champ_summoner_game table
query = "CREATE TABLE IF NOT EXISTS champ_summoner_game (" + \
        "matchId INT(15) UNSIGNED);"
if debug: print query
else: cursor.execute(query)

# add general match info columns to champ_summoner_game table
query = genQueryAlterTable( 'champ_summoner_game', match['participants'][0],
        None)
if debug: print query
else: cursor.execute(query)

# add summoner stats to champ_summoner_game_table
query = genQueryAlterTable( 'champ_summoner_game',
        match['participants'][0]['stats'], None)
if debug: print query
else: cursor.execute(query)

# disconnect from server
db.close()
