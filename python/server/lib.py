#!/usr/bin/python
# a library of useful functions
import os
import json
import subprocess
import time
import MySQLdb

dir = os.path.dirname(__file__) # get absolute file path
data_dir = os.path.join(dir, '../../data/')
shell_dir = os.path.join(dir, '../../shell/')
private_dir = os.path.join(dir, '../../private/')

def createTables(debug=False):
    "function to creat db structure"
    # load database cretentials
    db_creds = json_load('db.json', private_dir)
    user_lvl = 2 # all privileges

    # load match data
    match = json_load('2117389806_match.json')

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
            "matchId INT(11) UNSIGNED, summonerId INT(11) UNSIGNED," +\
            "opposingTeam TINYINT(1) UNSIGNED);"
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

    # add champion position to champ_game_table
    query = genQueryAlterTable( 'champ_summoner_game',
            match['participants'][0]['timeline'], None)
    if debug: print query
    else: cursor.execute(query)

    # disconnect from server
    db.close()
    return

def fetch_api( args ):
    "executes the shell script getJson.sh to fetch data from the lol api"
    shellfile = os.path.abspath( os.path.join( shell_dir, 'getJson.sh' ) )
    subprocess.call([shellfile] + args)
    time.sleep(1)
    return

def genQueryAlterTable(table_name, json_data, primary=None):
    "function to add columns to a table"
    query = "ALTER TABLE " + table_name
    for key in json_data:
        if type(json_data[key]) is int:
            query += " ADD " + key + " INT(11) UNSIGNED"
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

def genQueryInsert(table_name, json_data):
    "function to insert values into a table"
    query = "INSERT INTO " + table_name + "("
    for key in json_data:
        if type(json_data[key]) is bool or \
            type(json_data[key]) is int or \
            type(json_data[key]) is str or \
            type(json_data[key]) is unicode:
            query += key + ","
    query = query[:-1]
    query += ") VALUES ("
    for key in json_data:
        if type(json_data[key]) is bool:
            query += str(int(json_data[key])) + ","
        elif type(json_data[key]) is int:
            query += str(json_data[key]) + ","
        elif type(json_data[key]) is str or type(json_data[key]) is unicode:
            query += "'" + json_data[key] + "',"
    query = query[:-1]
    query += ");"
    return query

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

def updateGame(gameId, win, opponent, debug=False):
    "function to the database with thje data of a game"

    # load database cretentials
    db_creds = json_load('db.json', private_dir)
    user_lvl = 1 # only SELECT, INSERT, UPDATE

    # load match data
    match = json_load(str(gameId) + '_match.json')
    members = json_load('summoners.json')

    # Open database connection
    db = MySQLdb.connect(
        db_creds['host'],
        db_creds['users'][user_lvl]['name'],
        db_creds['users'][user_lvl]['password'],
        db_creds['name']
    )

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # add columns to games table
    match['win'] = win
    match['opposingTeamName'] = opponent
    match['matchCreation'] = match['matchCreation']/1000
    query = genQueryInsert('games', match)
    if debug: print query
    else: cursor.execute(query)

    for guy in match['participants']:
        json_temp = guy.copy()
        json_temp.update(guy['stats'])
        if 'timeline' in guy: json_temp.update(guy['timeline'])
        json_temp['matchId'] = gameId
        for guyId in match['participantIdentities']:
            if guyId['participantId'] == guy['participantId']:
                json_temp['summonerId'] = guyId['player']['summonerId']
                break
        json_temp['opposingTeam'] = True
        if str(json_temp['summonerId']) in members:
            json_temp['opposingTeam'] = False
        query = genQueryInsert('champ_summoner_game', json_temp)
        if debug: print query
        else: cursor.execute(query)

    db.commit()
    print "saved data from match " + str(gameId) + " to database\n"
    # disconnect from server
    db.close()
    return
