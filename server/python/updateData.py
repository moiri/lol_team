#!/usr/bin/python
# fetch team and roster data and update the local files if necessary. Also
# fetch the new match history and update the db with the new matches

import lib_server as lib
import os

matches = []

# get new team match history and team roster, update the json files
team_new = lib.api_getTeam( lib.myTeamId )
roster = lib.api_getTeamRoster(team_new)

# update champion file
lib.api_fetch(['-c', '-o', lib.data_dir + "champion.json"])

for match in team_new['matchHistory']:
    # if there is already a match.json file go to the next id
    if os.path.isfile(lib.data_dir + str(match['gameId']) + '_match.json'):
        continue

    try:
        matchDetails = lib.api_getMatchDetails(match['gameId'],
                match['opposingTeamName'], roster)
    except:
        print "ERROR: Could not fetch match " + str(match['gameId']) + "\n"
        continue
    matches.append(matchDetails)


# insert new matches into the DB
lib.db_insertMatches(matches, roster)
