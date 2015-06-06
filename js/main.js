$(document).ready(function() {
    var data = {};
    data.summonerId = null;
    data.opposingTeam = '0';
    data.role = null;
    $.getJSON('data/team.json', function(team) {
        $.getJSON('data/summoners.json', function(summoners) {
            var cb;
            $('.summoners').append(
                '<li><a id="summoner-all" href="#">' + team.name + '</a></li>'
                + '<li role="presentation" class="divider"></li>'
            );
            $.each(team.roster.memberList, function (idx, member) {
                $('.summoners').append(
                    '<li><a id="summoner-' + member.playerId
                    + '" href="#">' + summoners[member.playerId] + '</a></li>'
                );
            });
            $('.summoners').append(
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
                    cb = enable_sum_filter;
                }
                else if (id[1] === 'all') {
                    summonerName = team.name;
                    cb = disable_sum_filter;
                }
                else {
                    data.summonerId = id[1];
                    summonerName = summoners[id[1]]
                    cb = enable_sum_filter;
                }

                getWinrate(data, summonerName, cb);
            });
            $('[id|="role"]').click(function() {
                var me = $(this);
                data.role = null;
                id = me.attr('id').split('-');
                data.role = id[1];
                getWinrate(data, undefined, function () {
                    $('#filter-role button span:first').html(me.html())
                    $('#filter-role').show();
                });
            });
            $('[id|="filter"] button:not(disabled)').click(function() {
                var summonerName, cb, me = $(this);
                id = me.parent().attr('id').split('-');
                if (id[1] === "summonerId") {
                    summonerName = team.name;
                    cb = disable_sum_filter;
                    data.opposingTeam = null;
                }
                else cb = function () { me.parent().hide(); }
                data[id[1]] = null;
                getWinrate(data, summonerName, cb);
            });
            getWinrate(data, team.name, disable_sum_filter);
        });
    });
});

function getWinrate(data, summonerName, cb) {
    var url;
    url = 'python/stats/stats_champions';
    $.getJSON(url, data, function(json) {
        var table_title;

        if (summonerName != undefined) {
            $('#title-name').html(summonerName);
            $('#filter-summonerId button span:first').html(summonerName);
            $('#filter-summonerId').show();
        }
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
        if (json.champions.length) {
            $("table#champs").tablesorter({
                // sort on the first column and third column, order asc 
                sortList: [[1,1]]
            });
        }
        if (cb != undefined) cb();
    });
}


function enable_sum_filter () {
    $('#filter-summonerId button').removeAttr('disabled');
    $('#filter-summonerId button').children('span:last').show();
}
function disable_sum_filter () {
    $('#filter-summonerId button').attr('disabled', 'disabled');
    $('#filter-summonerId button').children('span:last').hide();
}
