$(document).ready(function() {
    var data = {};
    data.summonerId = null;
    data.opposingTeam = '0';
    data.lane = null;
    $.getJSON('data/team.json', function(team) {
        $('.header').html(
            team.name + " " + team.teamStatDetails[0].wins + ":"
            + team.teamStatDetails[0].losses
            + " (" + (team.teamStatDetails[0].wins
                      / (team.teamStatDetails[0].wins
                         + team.teamStatDetails[0].losses)).toFixed(2)
            + ")"
        );
        $.getJSON('data/summoners.json', function(summoners) {
            $.each(team.roster.memberList, function (idx, member) {
                $('.leftColumn').append(
                    '<div id="summoner-' + member.playerId
                    + '" class="summoner">' + summoners[member.playerId] + '</div>'
                );
            });
            $('.leftColumn').append(
                '<div id="summoner-opposingTeam" class="summoner opposingTeam">Opposing Team</div>'
            );
            $('.leftColumn').append(
                '<div id="clear" class="clear">clear</div>'
            );
            $('.summoner').click(function() {
                var id;
                data.opposingTeam = '0';
                data.summonerId = null;
                if (!$(this).hasClass('active')) {
                    $('.summoner').removeClass('active');
                    $(this).addClass('active');
                    id = $(this).attr('id').split('-');
                    if (id[1] === 'opposingTeam')
                        data.opposingTeam = '1'
                    else
                        data.summonerId = id[1];
                }
                else {
                    $(this).removeClass('active');
                }
                getWinrate(data);
            });
            $('.clear').click(function() {
                data = {};
                $('.summoner').removeClass('active');
                $('.filter').removeClass('active');
                getWinrate();
            });
            getWinrate();
        });
    });
});

function getWinrate(data) {
    var url;
    url = 'python/winrate/winrate_champions';
    $.getJSON(url, data, function(json) {
        $('.midColumn').html(
            '<table id="champs" class="tablesorter">' +
                '<thead><tr>' +
                    '<th>Name</th><th># Games</th><th># Wins</th><th>Win Rate</th>' +
                '</tr></thead><tbody></tbody>' +
            '</table>'
        );
        $.each(json.champions, function (idx, champion) {
            $('table#champs > tbody').append(
                '<tr id="champion-"' + champion.id + '>' +
                '<td>' + champion.name + '</td>' +
                '<td>' + champion.stats.gameCount + '</td>' +
                '<td>' + champion.stats.winCount + '</td>' +
                '<td>' + champion.stats.winRate + '</td>' +
                '</tr>'
            );
        });
        $("table#champs").tablesorter({
            // sort on the first column and third column, order asc 
            sortList: [[1,1]]
        });
        $('.midColumn').css({'margin-left': $('.leftColumn').outerWidth()});
        $('.midColumn').css({'margin-right': $('.rightColumn').outerWidth()});
    });
}
