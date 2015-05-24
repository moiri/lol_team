$(document).ready(function() {
    var url ;
    url = 'data/team.json';
    $.getJSON(url, function(json) {
        $.each(json.matchHistory, function (idx, match) {
            var css = 'loss';
            if (match.win) css = 'win';
            $('.leftColumn').append(
                '<div id="match-' + match.gameId + '" class="'+ css +'">'
                    + match.opposingTeamName + '</div>'
            );
        });
    });
});
