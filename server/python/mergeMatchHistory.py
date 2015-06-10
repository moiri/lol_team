#!/usr/bin/python
# This script merges the new match history with the locally stored json data and
# fetches new match data
import lib_server as lib

matches_new = []

# get new team match history
team_new = lib.getTeam( lib.myTeamId )

# load old team match history
team = lib.json_load( lib.myTeamFileName )

# merge match history
for match_new in team_new['matchHistory']:
    addElement = True
    for match in team['matchHistory']:
        if match_new['gameId'] == match['gameId']:
            addElement = False
            break;
    if addElement:
        matches_new.append(match_new)
        # add new history elements to old match history
        team['matchHistory'].append(match_new)
        addElement = False

# sort the match history
team['matchHistory'].sort(key=lambda match: match['date'], reverse=True)
# replace the (small) match history in the new file with the complete one
team_new['matchHistory'] = team['matchHistory'];

if len(matches_new) > 0:
    print str(len(matches_new)) + " new match history elements added\n"
else:
    print "nothing to update in mach history\n"

# save new team data to file (including the complete match history)
lib.json_dump( lib.myTeamFileName, team_new )

# fetch the new match files
for match_new in matches_new:
    # execute the shell script to fetch the match info
    lib.fetch_api(['-m', str(match_new['gameId'])])
    # execute the shell script to fetch the match info with timeline
    lib.fetch_api(['-m', str(match_new['gameId']), '-l'])
    # insert data
    lib.updateGame(match_new['gameId'], match_new['win'],
            match_new['opposingTeamName'])
