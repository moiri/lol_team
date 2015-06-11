#!/usr/bin/python
# setup the necessary stuff to get started

import lib_server as lib

# load team by ID and get summoner names
myTeam = lib.api_getTeam(lib.myTeamId)
roster = lib.api_getTeamRoster(myTeam)

# collect match history
matchHistory = lib.api_getTeamMatchHistory(myTeam, roster)

# create tables in the database
db_createTables(matchHistory[0])

# insert match history and match details into the db
db_insertMatches(matchHistory, roster)
