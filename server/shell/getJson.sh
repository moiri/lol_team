#!/bin/sh
set -e

PROGNAME=$(basename $0)

die() {
    echo "$PROGNAME: $*" >&2
    exit 1
}

usage() {
    if [ "$*" != "" ] ; then
        echo "Error: $*"
    fi

    cat << EOF

Usage: $PROGNAME [OPTION ...] [url]

Get JSON string from league of legends API server. If an explicit url is set,
all (*) parameters are ignored. If API usage is not specified with parameters
or an explicit url, status information are returned.

Options:
-h, --help                 display this usage message and exit
-a, --match-history [ID]   get match history by summoner ID
-r, --ranked-team          only get match history with ranked team games
-b, --begin-index [IDX]    get the match history (15 elements) beginning with
                           index [IDX]
-t, --team [ID]            get team info by ID (ID=0 selects the teamId from
                           the file ../private/team) (*)
-m, --match [ID]           get match info by ID (*)
-l, --timeline             add timeline to JSON object (*)
-s, --team-summoner [ID]   get teams by summoner ID
-p, --summoner [ID]        get summoner infos by comma seperated IDs
-c, --champion             get champion information
-o, --output [FILE]        write output to file

EOF

    exit 1
}
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")
key="api_key="$(cat $SCRIPTPATH/../private/key)
url_base="https://euw.api.pvp.net/api/lol/"
url_region="euw/"
url_api=""
option=""
url=""
id=""
output=""
output_def="status"
output_suffix=""
output_path="../../data/"
my_date=$(echo $(date +%Y%m%d-%H%M%S))
while [ $# -gt 0 ] ; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -a|--match-history)
            url_api="v2.2/matchhistory/"
            id=$2
            if [ -z "$id" ] ; then
                usage "ID required"
            fi
            output_def=${id}_history
            shift
            ;;
        -b|--begin-index)
            if [ -z "$2" ] ; then
                usage "IDX required"
            fi
            option="${option}beginIndex=${2}&"
            output_suffix=${output_suffix}_${2}
            shift
            ;;
        -r|--ranked-team)
            option="${option}rankedQueues=RANKED_TEAM_5x5&"
            output_suffix="${output_suffix}_team"
            ;;
        -t|--team)
            url_api="v2.4/team/"
            id=$2
            if [ "$id" = "0" ] ; then
                id=$(cat $SCRIPTPATH/../private/team)
            fi
            shift
            # output_def=${my_date}_${id}_team
            output_def="teams_new"
            ;;
        -m|--match)
            url_api="v2.2/match/"
            id=$2
            if [ -z "$id" ] ; then
                usage "ID required"
            fi
            output_def=${id}_match
            shift
            ;;
        -l|--timeline)
            option="${option}includeTimeline=true&"
            output_suffix="${output_suffix}_timeline"
            ;;
        -s|--team-summoner)
            url_api="v2.4/team/by-summoner/"
            id=$2
            if [ -z "$id" ] ; then
                usage "ID required"
            fi
            output_def=${id}_team
            shift
            ;;
        -p|--summoner)
            url_api="v1.4/summoner/"
            id=$2
            if [ -z "$id" ] ; then
                usage "ID required"
            fi
            output_def="summoners"
            shift
            ;;
        -c|--champion)
            url_api="v1.2/champion/"
            url_base="https://global.api.pvp.net/api/lol/static-data/"
            output_def="champion"
            ;;
        -o|--output)
            output="$2"
            shift
            ;;
        -*)
            usage "Unknown option '$1'"
            ;;
        *)
            if [ -n "$1" ] ; then
                url=$1
            fi
            ;;
    esac
    shift
done

if [ -n "$url" ] ; then
    echo use explicit url
elif [ -z "$url_api" ] ; then
    url_api="status"
    output_def=${my_date}_status
    url="http://status.leagueoflegends.com/shards"
else
    url=$url_base$url_region$url_api$id?$option$key
fi
if [ -z "$output" ]; then
    output=${SCRIPTPATH}/${output_path}${output_def}${output_suffix}.json
fi

echo "fetch data from API: $url_base$url_region${url_api}${id}?${option}key=..."
json=$(curl --request GET $url)
output=$(readlink -m $output)
echo "saved in file "$output"\n"
echo $json > $output
