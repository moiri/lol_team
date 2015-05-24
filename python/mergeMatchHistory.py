# This script merges the new match history with the locally stored json data

import json
import os
import sys
import subprocess
import time

dir = os.path.dirname(__file__) # get absolute file path

# execute the shell script to fetch the new team match history
shellfile = os.path.join(dir, '../shell/getJson.sh')
infile = os.path.join(dir, '../data/teams_new.json')
subprocess.call([shellfile, '-t', str(0), '-o', infile])
time.sleep(1)

# load new match history as json file
with open(infile) as data_file:
    teams = json.load(data_file)

# only continue if there is one team inside the file
if len(teams) > 1:
    print "Only one team is expected but " + str(len(teams)) + \
        " are stored in the file"
    sys.exit()

for id in teams:
    team_new = teams[id]

# load old team match history
team_file = os.path.join(dir, '../data/team.json')
with open(team_file) as data_file:
    team = json.load(data_file)

# add new history elements to old match history and fetch match json files
counter=0
for match_new in team_new['matchHistory']:
    addElement = True
    for match in team['matchHistory']:
        if match_new['gameId'] == match['gameId']:
            addElement = False
            break;
    if addElement:
        # execute the shell script to fetch the match info
        subprocess.call([shellfile, '-m', str(match_new['gameId'])])
        time.sleep(1)
        # execute the shell script to fetch the match info with timeline
        subprocess.call([shellfile, '-m', str(match_new['gameId']), '-l'])
        time.sleep(1)
        # add new history elements to old match history
        team['matchHistory'].append(match_new)
        counter = counter + 1
        addElement = False

# if there were changes, update the history file
if counter > 0:
    print str(counter) + " new elements added"
    with open(team_file, 'w') as data_file:
        json.dump(team, data_file)
else:
    print "no new entries available"
