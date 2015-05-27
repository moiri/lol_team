#!/usr/bin/python
# this script uses a match.json file and extracts parts of the keys to generate
# a database structure. It then collects all maches from the team and fills up
# created tables with data

import lib

team_filename = 'team.json'
lib.createTables()
# load old team match history
team = lib.json_load( team_filename )
# save match data in DB
for match in team['matchHistory']:
    lib.updateGame(match['gameId'], match['win'], match['opposingTeamName'])
