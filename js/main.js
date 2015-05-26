$(document).ready(function() {
    var url ;
    url = 'data/team.json';
    $.getJSON(url, function(team) {
        $('.header').html(
            team.name + " " + team.teamStatDetails[0].wins + ":"
            + team.teamStatDetails[0].losses
            + " (" + (team.teamStatDetails[0].wins
                      / (team.teamStatDetails[0].wins
                         + team.teamStatDetails[0].losses)).toFixed(2)
            + ")"
        );
    });
    url = 'data/summoners.json';
    $.getJSON(url, function(summoners) {
        $.each(summoners, function (id, name) {
            $('.leftColumn').append(
                '<div id="summoner-' + id + '" class="summoner">' + name + '</div>'
            );
        });
        $('.leftColumn').append(
            '<div id="summoner-0" class="summoner clear">clear</div>'
        );
        $('.summoner').click(function(){
            $('.summoner').removeClass('active');
            $(this).toggleClass('active');
            id = $(this).attr('id').split('-');
            if (id[1] === '0')
                getWinrate();
            else
                getWinrate(id[1]);
        });
    });
    getWinrate();
});

function getWinrate(summonerId) {
    var url, data;
    url = 'python/winrate/winrate_champions';
    $.getJSON(url, { summonerId: summonerId }, function(json) {
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
    });
}
