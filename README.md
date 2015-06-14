This project aims to provide a set of scripts to collect match data of a League
of Legends Team. The [Riot API](https://developer.riotgames.com/) provides an
interface to fetch all kind of data but does not include a complete team
history. It is only possible to fetch the last 20 games of the team.

I can see two possible reasons as to why this might be the case:
 * Solo-queue is the main thing, teams are relatively unimportant.
 * Team statistics might lead to conclusions about certain players and
 provoke unjustified expulsions from the team.

Well, I was interested in the statistics of my team and went through the
trouble of collecting the data. I used the scripts provided here to do so.

# Collect Team Match History
The python script **setup** collects the team data of *myTeam*, the summoner
details of the roster of *myTeam*, the match history of *myTeam*, generates
DB tables (MySQL) and saves the collected data in the tables.

The python function **api_getTeamMatchHistory** collects the *myTeam* match
history by
 * collecting all teams of every summoner in the roster of *myTeam*
 * collecting match IDs of all *otherTeams* from their history (only 20 games)
 * collecting team matches from each summoner

The game is assumed to be from *myTeam* if
 * the ID does not match a game from one of the *otherTeams*
 * the *myTeam* join date of the summoner we are currently investigating the
   history is lower than the game creation date
 * one team of the game consist fully of players from the roster of *myTeam*

This approach is not perfect because
 * a summoner could be in the roster of two teams with very similar rosters
 * the cross check with the *otherTeam* history can only be done over the last
   20 matches
 * the roster of teams can change over time

# Update Team Match History
The python script **updateDate** uses the 20 item history of the team data to
consecutively update the DB with new game information. Once the DB tables are
created and initialised (**setup** script) the **update** script can be run
on e.g. hourly basis by a cron job.
