$(document).ready(function() {
    var data = {};
    data.summonerId = null;
    data.opposingTeam = '0';
    data.role = null;
    data.minCount = 0;
    $.getJSON('data/team.json', function(team) {
        $.getJSON('data/summoners.json', function(summoners) {
            var cb;
            $('.summoners').append(
                '<li><a id="summonerId-all" href="#">' + team.name + '</a></li>'
                + '<li role="presentation" class="divider"></li>'
            );
            $.each(team.roster.memberList, function (idx, member) {
                $('.summoners').append(
                    '<li><a id="summonerId-' + member.playerId
                    + '" href="#">' + summoners[member.playerId] + '</a></li>'
                );
            });
            $('.summoners').append(
                '<li role="presentation" class="divider"></li>'
                + '<li><a id="summonerId-opposingTeam" href="#">Opponents</a></li>'
            );
            $('[id|="summonerId"]').click(function() {
                var id, summonerName;
                data.opposingTeam = '0';
                data.summonerId = null;

                id = $(this).attr('id').split('-');
                if (id[1] === 'opposingTeam') {
                    data.opposingTeam = '1'
                    summonerName = "Opponents";
                    cb = function () {enable_filter(id[0]);}
                }
                else if (id[1] === 'all') {
                    summonerName = team.name;
                    cb = function () {disable_filter(id[0]);}
                }
                else {
                    data.summonerId = id[1];
                    summonerName = summoners[id[1]]
                    cb = function () {enable_filter(id[0]);}
                }

                getWinrate(data, summonerName, cb);
            });
            $('[id|="role"]').click(function() {
                var cb, me = $(this);
                data.role = null;
                id = $(this).attr('id').split('-');
                cb = function () {hide_filter(id[0]);}
                if (id[1] != 'all') {
                    data.role = id[1];
                    cb = function () {show_filter(id[0], me.html());}
                }
                getWinrate(data, undefined, cb);
            });
            $('[id|="minCount"]').click(function() {
                var me = $(this), cb;
                data.minCount = null;
                id = me.attr('id').split('-');
                cb = function () {hide_filter(id[0]);}
                if (id[1] != 'all') {
                    data.minCount = id[1];
                    cb = function () {show_filter(id[0], 'Min ' + me.html() + ' Games');}
                }
                getWinrate(data, undefined, cb);
            });
            $('[id|="filter"] > button:not(disabled)').click(function() {
                var summonerName, cb;
                id = $(this).parent().attr('id').split('-');
                cb = function () { hide_filter(id[1]); }
                if (id[1] === "summonerId") {
                    summonerName = team.name;
                    cb = function () {disable_filter(id[1]);}
                    data.opposingTeam = null;
                }
                data[id[1]] = null;
                getWinrate(data, summonerName, cb);
            });
            getWinrate(data, team.name, function () {disable_filter('summonerId');});
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

function show_filter (id, data) {
    $('#filter-' + id + ' > button > span:first').html(data)
    $('#filter-' + id).show();
}

function hide_filter (id) {
    $('#filter-' + id).hide();
}

function enable_filter (id) {
    $('#filter-' + id + ' > button').removeAttr('disabled');
    $('#filter-summonerId > button').children('span:last').show();
}
function disable_filter (id) {
    $('#filter-' + id + ' > button').attr('disabled', 'disabled');
    $('#filter-' + id + ' > button').children('span:last').hide();
}
