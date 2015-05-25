#!/usr/bin/python
import lib
import json
import MySQLdb

def winrate_summoners():
    # lead team and summoner information
    team = lib.json_load('team.json', '../data/')
    summoners = lib.json_load('summoners.json', '../data/')

    # load database cretentials
    db_creds = lib.json_load('db.json', '../private/')
    user_lvl = 0 # only SELECT

    # Open database connection
    db = MySQLdb.connect(
        db_creds['host'],
        db_creds['users'][user_lvl]['name'],
        db_creds['users'][user_lvl]['password'],
        db_creds['name']
    )
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    json_data = {}
    json_data['members'] = []
    for member in team['roster']['memberList']:
        query = "SELECT winner FROM champ_summoner_game WHERE summonerId='" + \
                str(member['playerId']) + "';"
        cursor.execute(query)

        rows = cursor.fetchall()
        winCount = 0
        for row in rows:
            winCount += row[0]

        player = {}
        player['id'] = member['playerId']
        player['name'] = summoners[str(member['playerId'])]
        player['stats'] = {}
        player['stats']['gameCount'] = len(rows)
        player['stats']['winCount'] = winCount
        player['stats']['winRate'] = float(winCount) / float(len(rows))
        json_data['members'].append(player)

    # disconnect from server
    db.close()
    return json.dumps(json_data)

def winrate_champions():
    # load team information
    team = lib.json_load('team.json', '../data/')
    championStats = lib.json_load('champion.json', '../data/')

    # load database cretentials
    db_creds = lib.json_load('db.json', '../private/')
    user_lvl = 0 # only SELECT

    # Open database connection
    db = MySQLdb.connect(
        db_creds['host'],
        db_creds['users'][user_lvl]['name'],
        db_creds['users'][user_lvl]['password'],
        db_creds['name']
    )
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    query = "SELECT DISTINCT championId FROM champ_summoner_game;"
    cursor.execute(query)
    champIds = cursor.fetchall()

    json_data = {}
    json_data['champions'] = []
    for champId in champIds:
        query = "SELECT winner FROM champ_summoner_game WHERE championId='" + \
                str(champId[0]) + "';"
        cursor.execute(query)
        rows = cursor.fetchall()
        winCount = 0
        for row in rows:
            winCount += row[0]

        for key in championStats['data']:
            if championStats['data'][key]['id'] == champId[0]:
                name = championStats['data'][key]['name']
        champion = {}
        champion['id'] = champId[0]
        champion['name'] = name
        champion['stats'] = {}
        champion['stats']['gameCount'] = len(rows)
        champion['stats']['winCount'] = winCount
        champion['stats']['winRate'] = round(float(winCount) / float(len(rows)), 2)
        json_data['champions'].append(champion)

    # disconnect from server
    db.close()
    # json_data['champions'].sort(key=lambda champ: champ['stats']['gameCount'], reverse=True)
    return json.dumps(json_data)
