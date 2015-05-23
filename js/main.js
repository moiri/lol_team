$(document).ready(function() {
    var url, teams = [];
    url = 'data/teams.json';
    $.getJSON(url, function(json) {
        for (id in json) teams.push(id);
        $.each(json[teams[0]].matchHistory, function (idx, match) {
            var css = 'loss';
            if (match.win) css = 'win';
            $('.leftColumn').append(
                '<div id="match-' + match.gameId + '" class="'+ css +'">'
                    + match.opposingTeamName + '</div>'
            );
        });
    });
});
