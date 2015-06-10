# This script collects the missing data from the old matches and completes the
# match history entry of the team.json file.
# This file was used only once, know it generates the file test_team.json to not
# overwrite the team.json file

import lib_server as lib
import os


# load team by ID and get summoner names
myTeam = lib.getTeam(lib.myTeamId)
roster = lib.getTeamRoster(myTeam)

# if there is already a team.json file use the history from this file
if os.path.isfile(lib.data_dir + lib.myTeamFileName):
    tempTeam = lib.json_load(lib.myTeamFileName, lib.data_dir)
    myTeam['matchHistory'] = tempTeam['matchHistory']
else:
    # clean history
    myTeam['matchHistory'] = []


# iterate through summoners and collect other team data
gameIds = []
idList = ""
for summonerId in roster:
    idList += summonerId + ","
idList[:-1]
lib.fetch_api(['-s', idList, '-o', lib.data_dir + 'teams_summoners.json'])
sTeams = lib.json_load('teams_summoners.json', lib.data_dir)

# collect match Ids from myTeam
opposingTeamNames = {}
myMatchIds = [] # all match IDs of myTeam (after all is said and done)
for match in myTeam['matchHistory']:
    if match['gameId'] not in myMatchIds:
        myMatchIds.append(match['gameId'])
        opposingTeamNames[match['gameId']] = match['opposingTeamName']

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
        lib.fetch_api(['-a', summonerId, '-b', str(idx), '-r'])
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
                matchDetails = lib.getMatchDetails(match['matchId'],
                        opposingTeamName,
                        match['participants'][0]['teamId'],
                        roster)

                if matchDetails['valid']:
                    print "add data from match " + str(match['matchId']) + " to history\n"
                    myTeam['matchHistory'].append(matchDetails)
                else:
                    print "player missmatch: not all players from match " \
                        + str(match['matchId']) + " are part of the roaster\n"
        idx += 15

# sort the match history
myTeam['matchHistory'].sort(key=lambda match: match['date'], reverse=True)
# save match history to file
lib.json_dump(lib.myTeamFileName, myTeam, lib.data_dir)

