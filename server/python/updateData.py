#!/usr/bin/python
# fetch team data update local files if necessary also
# fetch the new match history and update the db with the
# new matches

import lib_server as lib
import os

matches = []

# get new team match history and update team roster
team_new = lib.getTeam( lib.myTeamId )
roster = lib.api_getTeamRoster(team_new)

for match in team_new['matchHistory']:
    # if there is already a match.json file go to the next id
    if os.path.isfile(lib.data_dir + str(match['gameId']) + '_match.json'):
        continue

    matchDetails = lib.api_getMatchDetails(match['gameId'],
            match['opposingTeamName'], roster)
    matches.append(matchDetails)

# insert new matches into the DB
db_insertMatches(matches, roster)

# update team json file
del team_new['matchHistory']
lib.json_dump(lib.myTeamFileName, lib.data_dir)
