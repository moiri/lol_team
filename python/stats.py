#!/usr/bin/python
import sys
import os
dir = os.path.dirname(__file__) # get absolute file path
sys.path.insert(0, os.path.join(dir, 'server'))
import lib
import json
import MySQLdb
import mod_python

def winrate_summoners():
    # lead team and summoner information
    team = lib.json_load('team.json')
    summoners = lib.json_load('summoners.json')

    # load database cretentials
    db_creds = lib.json_load('db.json', private_dir)
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

def stats_champions(req):
    # load team information
    user_data = mod_python.util.FieldStorage(req)
    summonerId = None
    if 'summonerId' in user_data:
        summonerId = user_data['summonerId'].value
    opposingTeam = '0';
    if 'opposingTeam' in user_data:
        opposingTeam = user_data['opposingTeam'].value
    lane = None
    if 'lane' in user_data:
        lane = user_data['lane'].value
    team = lib.json_load('team.json')
    championStats = lib.json_load('champion.json')

    # load database cretentials
    db_creds = lib.json_load('db.json', lib.private_dir)
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

    query_where_clause = " AND opposingTeam='" + opposingTeam + "'"
    if summonerId:
        query_where_clause += " AND summonerId='" + summonerId + "'"
    if lane:
        query_where_clause += " AND lane='" + lane + "'"
    query = "SELECT DISTINCT championId FROM champ_summoner_game WHERE 1"
    query += query_where_clause + ';'
    cursor.execute(query)
    champIds = cursor.fetchall()

    json_data = {}
    json_data['champions'] = []
    json_data['fields'] = ['Name', '# Games', '# Wins', 'Win Rate', "Kills", 
            "Deaths", "Assists", "KDA", "Gold", "CS"]
    for champId in champIds:
        query = "SELECT winner, kills, deaths, assists, goldEarned," \
                + " minionsKilled, neutralMinionsKilled" \
                + " FROM champ_summoner_game" \
                + " WHERE championId='" + str(champId[0]) + "'" \
                + query_where_clause + ';'
        cursor.execute(query)
        rows = cursor.fetchall()
        winCount = 0
        kill_sum = 0
        death_sum = 0
        assist_sum = 0
        gold_sum = 0
        cs_sum = 0
        for row in rows:
            winCount += row[0]
            kill_sum += row[1]
            death_sum += row[2]
            assist_sum += row[3]
            gold_sum += row[4]
            cs_sum += row[5] + row[6]

        for key in championStats['data']:
            if championStats['data'][key]['id'] == champId[0]:
                name = championStats['data'][key]['name']
        champion = {}
        champion['id'] = champId[0]
        champion['name'] = name
        champion['stats'] = []
        champion['stats'].append(len(rows))
        champion['stats'].append(winCount)
        champion['stats'].append(round(float(winCount) / float(len(rows)), 2))
        champion['stats'].append(round(float(kill_sum) / float(len(rows)), 1))
        champion['stats'].append(round(float(death_sum) / float(len(rows)), 1))
        champion['stats'].append(round(float(assist_sum) / float(len(rows)), 1))
        kda = "Infinity"
        if death_sum > 0:
            kda = round(float(kill_sum + assist_sum) / float(death_sum), 2)
        champion['stats'].append(kda)
        champion['stats'].append(round(float(gold_sum) / float(len(rows))))
        champion['stats'].append(round(float(cs_sum) / float(len(rows))))
        json_data['champions'].append(champion)

    # disconnect from server
    db.close()
    # json_data['champions'].sort(key=lambda champ: champ['stats']['gameCount'], reverse=True)
    return json.dumps(json_data)