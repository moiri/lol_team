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

def api_fetch( args ):
    "executes the shell script getJson.sh to fetch data from the lol api"
    shellfile = os.path.abspath( os.path.join( shell_dir, 'getJson.sh' ) )
    subprocess.call([shellfile] + args)
    time.sleep(lib.waitingTime)
    return

def api_getMatchDetails(matchId, opposingTeamName, roster, teamId=None, check=False):
    "return a dict with match details"

    # fetch match data if the file is not yet available
    if not os.path.isfile(lib.data_dir + str(matchId) + '_match.json'):
        api_fetch(['-m', str(matchId)])
    match = lib.json_load(str(matchId) + "_match.json", lib.data_dir)

    if not teamId:
        guyId = None
        for guy in match['participantIdentities']:
            if guy['player']['summonerId'] in roster:
                guyId = guy['participantId']
                break
        for guy in match['participants']:
            if guyId == guy['participantId']:
                teamId = guy['teamId']

    stats = {
        'kills': -1,
        'deaths': -1,
        'assists': -1,
        'oKills': -1,
        'oDeaths': -1,
        'oAssists': -1,
        'firstBlood': None,
        'firstTower': None,
        'firstInhibitor': None,
        'firstBaron': None,
        'firstDragon': None,
        'towerKills': -1,
        'inhibitorKills': -1,
        'baronKills': -1,
        'dragonKills': -1,
        'oTowerKills': -1,
        'oInhibitorKills': -1,
        'oBaronKills': -1,
        'oDragonKills': -1
    }
    myTeamParticipantIds = [];
    if 'participants' in match:
        stats['kills'] = 0
        stats['deaths'] = 0
        stats['assists'] = 0
        stats['oKills'] = 0
        stats['oDeaths'] = 0
        stats['oAssists'] = 0

        for guy in match['participants']:
            if (guy['teamId'] == teamId) and ('stats' in guy):
                stats['kills'] += 0 if 'kills' not in guy['stats'] else guy['stats']['kills']
                stats['deaths'] += 0 if 'deaths' not in guy['stats'] else guy['stats']['deaths']
                stats['assists'] += 0 if 'assists' not in guy['stats'] else guy['stats']['assists']
                myTeamParticipantIds.append(guy['participantId'])
            else:
                stats['oKills'] += 0 if 'kills' not in guy['stats'] else guy['stats']['kills']
                stats['oDeaths'] += 0 if 'deaths' not in guy['stats'] else guy['stats']['deaths']
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
                stats['towerKills'] = -1 if 'towerKills' not in team else team['towerKills']
                stats['inhibitorKills'] = -1 if 'towerKills' not in team else team['inhibitorKills']
                stats['baronKills'] = -1 if 'baronKills' not in team else team['baronKills']
                stats['dragonKills'] = -1 if 'dragonKills' not in team else team['dragonKills']
            else:
                stats['oTowerKills'] = -1 if 'towerKills' not in team else team['towerKills']
                stats['oInhibitorKills'] = -1 if 'towerKills' not in team else team['inhibitorKills']
                stats['oBaronKills'] = -1 if 'baronKills' not in team else team['baronKills']
                stats['oDragonKills'] = -1 if 'dragonKills' not in team else team['dragonKills']

    # check whether the team consists of 5 members of myTeam to narrow down the
    # possibility of getting a match of a different team  where the summoner is
    # also in the roster of myTeam
    valid = True
    memberCount = 0
    if check:
        for guy in match['participantIdentities']:
            if guy['participantId'] in myTeamParticipantIds:
                if str(guy['player']['summonerId']) in roster:
                    memberCount += 1
        if memberCount != 5:
            # all 5 players need to be part of myTeam
            valid = False

    matchDetails = {
        'matchId': int(matchId),
        'matchCreation': match['matchCreation']/1000,
        'matchDuration': match['matchDuration'],
        'matchTeamId' : teamId,
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
        'oName': "n/a" if not opposingTeamName else opposingTeamName,
        'oKills': stats['oKills'],
        'oDeaths': stats['oDeaths'],
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

def api_getTeam(myTeamId):
    "get the team json file from the RIOT API"
    # fetch team json file
    api_fetch(['-t', myTeamId, '-o', lib.data_dir + myTeamId + "_team.json"])

    # extract team from json file
    myTeams = lib.json_load(myTeamId + "_team.json", lib.data_dir)
    if len(myTeams) > 1:
        print "Only one team is expected but " + str(len(teams_new)) + \
            " are stored in the file"
        sys.exit()
    for id in myTeams:
        myTeam = myTeams[id]

    return myTeam

def api_getTeamMatchHistory(myTeam, roster):
    "get the complete match history of the team. To this all summoner \
    history files are searched and filterd for team matches. To decide \
    if it is the right team, join dates are compared with match dates \
    and the match participants are compared with the team roster."
    # iterate through summoners and collect other team data
    idList = ""
    for summonerId in roster:
        idList += summonerId + ","
    idList[:-1]
    api_fetch(['-s', idList, '-o', lib.data_dir + 'teams_summoners.json'])
    sTeams = lib.json_load('teams_summoners.json', lib.data_dir)

    opposingTeamNames = {}
    myMatchIds = [] # all match IDs of myTeam (after all is said and done)
    # collect opposing team name where is is available
    for match in myTeam['matchHistory']:
        if match['gameId'] not in opposingTeamNames:
            opposingTeamNames[match['gameId']] = match['opposingTeamName']
    del myTeam['matchHistory']
    lib.json_dump(lib.myTeamFileName, myTeam, lib.data_dir)
    myTeam['matchHistory'] = []

    # collect further match Ids by searching the match history of sumoners in the
    # team roaster
    otherMatchIds = [] # match IDS collected from other teams
    teamIds = [lib.myTeamId]
    for summonerId in sTeams:
        print "collect team matches from summoner " + str(summonerId)
        print "-------------------------------------------------\n"
        # collect match IDs from all other teams (ids to be excluded)
        for team in sTeams[summonerId]:
            if (team['fullId'] not in teamIds) \
                    and (team['lastGameDate'] > roster[summonerId]['joinDate']):
                teamIds.append(team['fullId'])
                for match in team['matchHistory']:
                    if (match['date'] > roster[summonerId]['joinDate']) \
                            and (match['gameId'] not in otherMatchIds):
                        otherMatchIds.append(match['gameId'])
        # get match history from summoner
        # do it until a game is older than the join date or no game is available
        idx = 0;
        done = False
        while not done:
            api_fetch(['-a', summonerId, '-b', str(idx), '-r'])
            history = lib.json_load(
                    summonerId + '_history_' + str(idx) + '_team.json', lib.data_dir)
            if 'matches' not in history:
                done = True
                break # next summoner

            for match in history['matches']:
                if match['matchCreation'] < roster[summonerId]['joinDate']:
                    # match occurred before join date of summoner: exit loops
                    done = True
                    break

                # use otherMatchIds to identify team games from other teams (this is
                # not perfect as the team match history is very limited)
                if (match['matchId'] not in otherMatchIds) \
                        and (match['matchId'] not in myMatchIds):
                    # we got a winner
                    myMatchIds.append(match['matchId'])

                    # fetch the match data
                    opposingTeamName = None
                    if match['matchId'] in opposingTeamNames:
                        opposingTeamName = opposingTeamNames[match['matchId']]
                    matchDetails = api_getMatchDetails(match['matchId'],
                            opposingTeamName,
                            roster,
                            match['participants'][0]['teamId'],
                            True)

                    if matchDetails['valid']:
                        print "add data from match " + str(match['matchId']) + " to history\n"
                        myTeam['matchHistory'].append(matchDetails)
                    else:
                        print "player missmatch: not all players from match " \
                            + str(match['matchId']) + " are part of the roaster\n"
            idx += 15

    # sort the match history
    myTeam['matchHistory'].sort(key=lambda match: match['matchCreation'], reverse=True)
    return myTeam['matchHistory']

def api_getTeamRoster(myTeam):
    "extract the roster IDs from the team and get the corresponding summoner names"
    idList = ""
    joinDates = {}
    for summoner in myTeam['roster']['memberList']:
        idList += str(summoner['playerId']) + ','
        joinDates[summoner['playerId']] = summoner['joinDate']
    idList[:-1]
    api_fetch(['-p', idList])

    roster = lib.json_load('summoners.json', lib.data_dir)

    # add team join dates
    for summonerId in roster:
        roster[summonerId]['joinDate'] = joinDates[int(summonerId)]
    # update file
    lib.json_dump(lib.summonersFileName, roster, lib.data_dir)

    return roster

def db_createTables(match, debug=False):
    "create the tables match and stats in the DB"
    # load database cretentials
    db_creds = lib.json_load('db.json', private_dir)
    user_lvl = 2 # all privileges

    # Open database connection
    db = MySQLdb.connect(
        db_creds['host'],
        db_creds['users'][user_lvl]['name'],
        db_creds['users'][user_lvl]['password'],
        db_creds['name']
    )

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # generate match table
    query = query_createTable('match', match, 'matchId')
    if (debug): print query
    else: cursor.execute(query)
    print "created table 'match' in the database\n"

    # generate stats table
    j_match = lib.json_load(str(match['matchId']) + '_match.json')
    stats = {}
    stats['matchId'] = 0
    stats['summonerId'] = 0
    stats['opposingTeam'] = False
    stats.update(j_match['participants'][0])
    stats.update(j_match['participants'][0]['stats'])
    stats.update(j_match['participants'][0]['timeline'])

    query = query_createTable('stats', stats)
    if (debug): print query
    else: cursor.execute(query)
    print "created table 'stats' in the database\n"

    # disconnect from server
    db.close()
    return

def db_insertMatches(matchHistory, roster, debug=False):
    "insert an arry of matches into the database"

    # load database cretentials
    db_creds = lib.json_load('db.json', private_dir)
    user_lvl = 1 # only SELECT, INSERT, UPDATE

    # Open database connection
    db = MySQLdb.connect(
        db_creds['host'],
        db_creds['users'][user_lvl]['name'],
        db_creds['users'][user_lvl]['password'],
        db_creds['name']
    )

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    for match in matchHistory:
        # add columns to match table
        query = query_insertRow('match', match)
        if (debug): print query
        else: cursor.execute(query)
        j_match = lib.json_load(str(match['matchId']) + '_match.json')

        for guy in j_match['participants']:
            stats = guy.copy()
            stats['matchId'] = match['matchId']
            stats['summonerId'] = 0
            stats['opposingTeam'] = False
            if 'stats' in guy: stats.update(guy['stats'])
            if 'timeline' in guy: stats.update(guy['timeline'])
            for guyId in j_match['participantIdentities']:
                if guyId['participantId'] == guy['participantId']:
                    stats['summonerId'] = guyId['player']['summonerId']
                    break
            stats['opposingTeam'] = True
            if str(stats['summonerId']) in roster:
                stats['opposingTeam'] = False

            query = query_insertRow('stats', stats)
            if (debug): print query
            else: cursor.execute(query)

        db.commit()
        print "saved data from match " + str(match['matchId']) + " to database\n"

    # disconnect from server
    db.close()
    return

def query_createTable(tableName, cols, primary=None):
    "generates a query string to create a table"
    query = "CREATE TABLE IF NOT EXISTS `" + tableName + "` ("
    for key in cols:
        if type(cols[key]) is int:
            query += "`" + key + "` INT(11) UNSIGNED"
            if key == primary:
                query += " PRIMARY KEY"
            else:
                query += " DEFAULT NULL"
            query += ","
        elif type(cols[key]) is str or type(cols[key]) is unicode:
            query += "`" + key + "` VARCHAR(50) DEFAULT NULL,"
        elif type(cols[key]) is bool or cols[key] == None:
            query += "`" + key + "` TINYINT(1) UNSIGNED DEFAULT NULL,"

    query = query[:-1]
    query += ");"
    return query

def query_insertRow(tableName, row):
    "generates a query string to insert a row into a table"
    query = "INSERT INTO `" + tableName + "` ("
    for key in row:
        if type(row[key]) is bool \
            or (type(row[key]) is int and not row[key] < 0) \
            or (type(row[key]) is str or type(row[key]) is unicode and row[key] != 'n/a'):
            query += key + ","
    query = query[:-1]
    query += ") VALUES ("
    for key in row:
        if type(row[key]) is bool:
            query += str(int(row[key])) + ","
        elif type(row[key]) is int and not row[key] < 0:
            query += str(row[key]) + ","
        elif type(row[key]) is str or type(row[key]) is unicode and row[key] != 'n/a':
            query += "'" + row[key] + "',"
    query = query[:-1]
    query += ");"
    return query
