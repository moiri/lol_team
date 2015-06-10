#!/usr/bin/python
# a library of useful server functions
import os
import sys
import json
import subprocess
import time
import MySQLdb

dir = os.path.dirname(__file__) # get absolute file path
shell_dir = os.path.join(dir, '../shell/')
sys.path.insert(0, os.path.join(dir, '../../python'))
import lib
json_load = lib.json_load
json_dump = lib.json_dump
private_dir = lib.private_dir
data_dir = lib.data_dir
myTeamId = lib.myTeamId
myTeamFileName = lib.myTeamFileName
summonersFileName = lib.summonersFileName
championsFileName = lib.championsFileName

def createTables(debug=False):
    "function to creat db structure"
    # load database cretentials
    db_creds = lib.json_load('db.json', private_dir)
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

def getTeam(myTeamId):
    "get the team json file from the RIOT API"
    # fetch team json file
    fetch_api(['-t', myTeamId, '-o', lib.data_dir + myTeamId + "_team.json"])

    # extract team from json file
    myTeams = lib.json_load(myTeamId + "_team.json", lib.data_dir)
    if len(myTeams) > 1:
        print "Only one team is expected but " + str(len(teams_new)) + \
            " are stored in the file"
        sys.exit()
    for id in myTeams:
        myTeam = myTeams[id]

    return myTeam

def getTeamRoster(myTeam):
    "extract the roster IDs from the team and get the corresponding summoner names"
    idList = ""
    joinDates = {}
    for summoner in myTeam['roster']['memberList']:
        idList += str(summoner['playerId']) + ','
        joinDates[summoner['playerId']] = summoner['joinDate']
    idList[:-1]
    fetch_api(['-p', idList])

    roster = lib.json_load('summoners.json', lib.data_dir)

    # add team join dates
    for summonerId in roster:
        roster[summonerId]['joinDate'] = joinDates[int(summonerId)]
    lib.json_dump('summoners.json', roster, lib.data_dir)

    return roster

def getMatchDetails(matchId, opposingTeamName, teamId, roster = None):
    "return a dict with match details"
    fetch_api(['-m', str(matchId)])
    match = lib.json_load(str(matchId) + "_match.json", lib.data_dir)

    stats = {
        'kills': 0,
        'deaths': 0,
        'assists': 0,
        'oAssists': 0,
        'firstBlood': None,
        'firstTower': None,
        'firstInhibitor': None,
        'firstBaron': None,
        'firstDragon': None,
        'towerKills': None,
        'inhibitorKills': None,
        'baronKills': None,
        'dragonKills': None,
        'oTowerKills': None,
        'oInhibitorKills': None,
        'oBaronKills': None,
        'oDragonKills': None
    }
    myTeamParticipantIds = [];
    if 'participants' in match:
        for guy in match['participants']:
            if (guy['teamId'] == teamId) and ('stats' in guy):
                stats['kills'] += 0 if 'kills' not in guy['stats'] else guy['stats']['kills']
                stats['deaths'] += 0 if 'deaths' not in guy['stats'] else guy['stats']['deaths']
                stats['assists'] += 0 if 'assists' not in guy['stats'] else guy['stats']['assists']
                myTeamParticipantIds.append(guy['participantId'])
            else:
                stats['oAssists'] += 0 if 'assists' not in guy['stats'] else guy['stats']['assists']

    if 'teams' in match:
        for team in match['teams']:
            if team['teamId'] == teamId:
                stats['win'] = team['winner']
                stats['firstBlood'] = None if 'firstBlood' not in team else team['firstBlood']
                stats['firstTower'] = None if 'firstTower' not in team else team['firstTower']
                stats['firstInhibitor'] = None if 'firstInhibitor' not in team else team['firstInhibitor']
                stats['firstBaron'] = None if 'firstBaron' not in team else team['firstBaron']
                stats['firstDragon'] = None if 'firstDragon' not in team else team['firstDragon']
                stats['towerKills'] = None if 'towerKills' not in team else team['towerKills']
                stats['inhibitorKills'] = None if 'towerKills' not in team else team['inhibitorKills']
                stats['baronKills'] = None if 'baronKills' not in team else team['baronKills']
                stats['dragonKills'] = None if 'dragonKills' not in team else team['dragonKills']
            else:
                stats['oTowerKills'] = None if 'towerKills' not in team else team['towerKills']
                stats['oInhibitorKills'] = None if 'towerKills' not in team else team['inhibitorKills']
                stats['oBaronKills'] = None if 'baronKills' not in team else team['baronKills']
                stats['oDragonKills'] = None if 'dragonKills' not in team else team['dragonKills']

    # check whether the team consists of 5 members of myTeam to narrow down the
    # possibility of getting a match of a different team  where the summoner is
    # also in the roster of myTeam
    valid = True
    memberCount = 0
    if roster:
        for guy in match['participantIdentities']:
            if guy['participantId'] in myTeamParticipantIds:
                if str(guy['player']['summonerId']) in roster:
                    memberCount += 1
        if memberCount != 5:
            # all 5 players need to be part of myTeam
            valid = False

    matchDetails = {
        'matchId': matchId,
        'matchCreation': match['matchCreation'],
        'matchDuration': match['matchDuration'],
        'win': stats['win'],
        'kills': stats['kills'],
        'deaths': stats['deaths'],
        'assists': stats['assists'],
        'firstBlood': stats['firstBlood'],
        'firstTower': stats['firstTower'],
        'firstInhibitor': stats['firstInhibitor'],
        'firstBaron': stats['firstBaron'],
        'firstDragon': stats['firstDragon'],
        'towerKills': stats['towerKills'],
        'inhibitorKills': stats['inhibitorKills'],
        'baronKills': stats['baronKills'],
        'dragonKills': stats['dragonKills'],
        'oName': opposingTeamName,
        'oAssists': stats['oAssists'],
        'oTowerKills': stats['oTowerKills'],
        'oInhibitorKills': stats['oInhibitorKills'],
        'oBaronKills': stats['oBaronKills'],
        'oDragonKills': stats['oDragonKills'],
        'mapId': match['mapId'],
        'season': match['season'],
        'region': match['region'],
        'platformId': match['platformId'],
        'matchVersion': None if 'matchVersion' not in match else match['matchVersion'],
        'queueType': match['queueType'],
        'matchMode': match['matchMode'],
        'matchType': match['matchType'],
        'valid': valid
    }

    return matchDetails

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

def updateGame(gameId, win, opponent, debug=False):
    "function to the database with thje data of a game"

    # load database cretentials
    db_creds = lib.json_load('db.json', private_dir)
    user_lvl = 1 # only SELECT, INSERT, UPDATE

    # load match data
    match = lib.json_load(str(gameId) + '_match.json')
    members = lib.json_load('summoners.json')

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
