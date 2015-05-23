# This script collects the missing data from the old matches and completes the
# match history entry of the team.json file.
# This file was used only once, know it generates the file test_team.json to not 
# overwrite the team.json file

import json
import os
import sys
from pprint import pprint

def getTeamParticipantId(match, team):
    "I put this in a function to easily brack a nested loop"
    for playerM in match['participantIdentities']:
        for playerT in team['roster']['memberList']:
            if playerM['player']['summonerId'] == playerT['playerId']:
                return playerM['participantId']


dir = os.path.dirname(__file__)
infile = os.path.join(dir, '../data/teams.json')
with open(infile) as data_file:
    teams = json.load(data_file)
infile = os.path.join(dir, '../data/matchId.json')
with open(infile) as data_file:
    matchIds = json.load(data_file)

if len(teams) > 1:
    print len(teams)
    sys.exit()

for id in teams:
    team = teams[id]

for gameId in matchIds['matchIds']:
    infile = os.path.join(dir, '../data/' + str(gameId) + '_match.json')
    with open(infile) as data_file:
        match = json.load(data_file)

    participantId = getTeamParticipantId(match, team)
    for player in match['participants']:
        if player['participantId'] == participantId:
            teamId = player['teamId']
            break;

    for teamM in match['teams']:
        if teamM['teamId'] == teamId:
            win = teamM['winner']
            break;

    team['matchHistory'].append(
            {
                'assists': None,
                'date': match['matchCreation'],
                'deaths': None,
                'gameId': gameId,
                'gameMode': match['matchMode'],
                'invalid': False,
                'kills': None,
                'mapId': match['mapId'],
                'opposingTeamKills': None,
                'opposingTeamName': None,
                'win': win
            }
        )

outfile = os.path.join(dir, '../data/test_team.json')
with open(outfile, 'w') as data_file:
    json.dump(team, data_file)

# pprint(team)

