$(document).ready(function() {
    var data = {};
    data.season = "SEASON2016";
    data.queueType = "RANKED_TEAM_5x5";
    $.getJSON('data/team.json', function(team) {
        $.getJSON('data/summoners.json', function(summoners) {
            var cb;
            $('.summoners').append(
                '<li><a id="summonerId-all" href="#">' + team.name + '</a></li>'
                + '<li role="presentation" class="divider"></li>'
            );
            $.each(summoners, function (id, summoner) {
                $('.summoners').append(
                    '<li><a id="summonerId-' + id
                    + '" href="#">' + summoner.name + '</a></li>'
                );
            });
            $('.summoners').append(
                '<li role="presentation" class="divider"></li>'
                + '<li><a id="summonerId-opposingTeam" href="#">Opponents</a></li>'
            );
            $('[id|="summonerId"]').click(function() {
                var id, summonerName;
                delete data.opposingTeam;
                delete data.summonerId;

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
                    summonerName = summoners[id[1]].name;
                    cb = function () {enable_filter(id[0]);}
                }

                getWinrate(data, summonerName, cb);
            });
            $('[id|="role"]').click(function() {
                var cb, me = $(this);
                delete data.role;
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
                delete data.minCount;
                id = me.attr('id').split('-');
                cb = function () {hide_filter(id[0]);}
                if (id[1] != 'all') {
                    data.minCount = id[1];
                    cb = function () {show_filter(id[0], 'Min ' + me.html() + ' Games');}
                }
                getWinrate(data, undefined, cb);
            });
            $('[id|="season"]').click(function() {
                var cb, me = $(this);
                delete data.season;
                id = $(this).attr('id').split('-');
                cb = function () {hide_filter(id[0]);}
                if (id[1] != 'all') {
                    data.season = id[1];
                    cb = function () {show_filter(id[0], me.html());}
                }
                getWinrate(data, undefined, cb);
            });
            $('[id|="queueType"]').click(function() {
                var cb, me = $(this);
                delete data.queueType;
                id = $(this).attr('id').split('-');
                cb = function () {hide_filter(id[0]);}
                if (id[1] != 'all') {
                    data.queueType = id[1];
                    cb = function () {show_filter(id[0], me.html());}
                }
                getWinrate(data, undefined, cb);
            });
            $('[id|="filter"] > button:not(disabled)').click(function() {
                var summonerName, cb;
                id = $(this).parent().attr('id').split('-');
                cb = function () { hide_filter(id[1]); }
                delete data[id[1]];
                if (id[1] === "summonerId") {
                    summonerName = team.name;
                    cb = function () {disable_filter(id[1]);}
                    delete data.opposingTeam;
                }
                if (id[1] === "clear") {
                    data = {};
                    summonerName = team.name;
                    cb = function () { 
                        $('[id|="filter"]:not(#filter-summonerId)').hide();
                        disable_filter('summonerId');
                    }
                }
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
            var table = '<tr id="champion-' + champion.id + '">'
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
        if ($.isEmptyObject(data)) hide_filter('clear');
    });
}

function show_filter (id, data) {
    $('#filter-' + id + ' > button > span:first').html(data)
    $('#filter-' + id).show();
    $('#filter-clear').show();
}

function hide_filter (id) {
    $('#filter-' + id).hide();
}

function enable_filter (id) {
    $('#filter-' + id + ' > button').removeAttr('disabled');
    $('#filter-summonerId > button').children('span:last').show();
    $('#filter-clear').show();
}
function disable_filter (id) {
    $('#filter-' + id + ' > button').attr('disabled', 'disabled');
    $('#filter-' + id + ' > button').children('span:last').hide();
}
