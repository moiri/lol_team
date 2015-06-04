$(document).ready(function() {
    var data = {};
    data.summonerId = null;
    data.opposingTeam = '0';
    data.lane = null;
    $.getJSON('data/team.json', function(team) {
        $.getJSON('data/summoners.json', function(summoners) {
            $('.sidebar').append(
                '<li><a id="summoner-all" href="#">' + team.name + '</a></li>'
                + '<li role="presentation" class="divider"></li>'
            );
            $.each(team.roster.memberList, function (idx, member) {
                $('.sidebar').append(
                    '<li><a id="summoner-' + member.playerId
                    + '" href="#">' + summoners[member.playerId] + '</a></li>'
                );
            });
            $('.sidebar').append(
                '<li role="presentation" class="divider"></li>'
                + '<li><a id="summoner-opposingTeam" href="#">Opponents</a></li>'
            );
            $('[id|="summoner"]').click(function() {
                var id, summonerName;
                data.opposingTeam = '0';
                data.summonerId = null;

                id = $(this).attr('id').split('-');
                if (id[1] === 'opposingTeam') {
                    data.opposingTeam = '1'
                    summonerName = "Opponents";
                }
                else if (id[1] === 'all')
                    summonerName = team.name;
                else {
                    data.summonerId = id[1];
                    summonerName = summoners[id[1]]
                }

                getWinrate(data, summonerName);
            });
            getWinrate(data, team.name);
        });
    });
});

function getWinrate(data, summonerName) {
    var url;
    url = 'python/stats/stats_champions';
    $.getJSON(url, data, function(json) {
        var table_title;

        $('#title-name').html(summonerName);
        $('#title-wins').html(json.summoner.wins);
        $('#title-losses').html(json.summoner.losses);
        $('#title-winRate').html(json.summoner.winRate);

        table_title = '<table id="champs" class="table table-striped table-condensed tablesorter">' +
                '<thead><tr>';
        for (attr in json.fields) {
            table_title += '<th>' + json.fields[attr] + '</th>';
        }
        table_title += '</tr></thead><tbody></tbody>' +
            '</table>'
        $('.content').html(table_title);
        $.each(json.champions, function (idx, champion) {
            var table = '<tr id="champion-"' + champion.id + '>'
                + '<td>' + champion.name + '</td>';
            for (attr in champion.stats) {
                if (champion.stats[attr] === "Infinity")
                    champion.stats[attr] = Infinity;
                table += '<td>' + champion.stats[attr] + '</td>';
            }
            table += '</tr>';
            $('table#champs > tbody').append(table);
        });
        $("table#champs").tablesorter({
            // sort on the first column and third column, order asc 
            sortList: [[1,1]]
        });
    });
}
