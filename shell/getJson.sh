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
-h, --help                display this usage message and exit
-t, --team [ID]           get team info by ID (default team: Laureicheibe) (*)
-m, --match [ID]          get match info by ID (*)
-l, --timeline            add timeline to JSON object (*)
-o, --output [FILE]       write output to file

EOF

    exit 1
}

key="api_key="$(cat ../private/key)
url_base="https://euw.api.pvp.net/api/lol/euw/"
url_api=""
option=""
url=""
id=""
output=""
output_def="status"
output_suffix=""
output_path="../data/"
my_date=$(echo $(date +%Y%m%d-%H%M%S))
while [ $# -gt 0 ] ; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -t|--team)
            url_api="v2.4/team/"
            id=$2
            if [ -z "$id" ] ; then
                id="TEAM-106e2ea0-959c-11e3-a2ca-782bcb497d6f"
            else
                shift
            fi
            output_def=${my_date}_${id}_team
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
            option="includeTimeline=true&"
            output_suffix="_timeline"
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
    output_def=${my_date}_status
    url="http://status.leagueoflegends.com/shards"
else
    url=$url_base$url_api$id?$option$key
fi
if [ -z "$output" ]; then
    output=${output_path}${output_def}${output_suffix}.json
fi

json=$(curl --request GET $url)
echo $json > $output
