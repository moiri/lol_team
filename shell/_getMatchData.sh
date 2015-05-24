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

Usage: $PROGNAME [OPTION ...] file

Utility script to fetch all matches with the IDs listed in a seperate file

Options:
-h, --help            display this usage message and exit
-d, --delay [FLOAT]   specify delay between two consecutive requests in seconds
                      (default: 1)

EOF

    exit 1
}

delay=1
file=""
while [ $# -gt 0 ] ; do
    case "$1" in
        -h|--help)
            usage
            ;;
        -d|--delay)
            delay=$2
            if [ -z "$delay" ] ; then
                usage "specify delay"
            fi
            shift
            ;;
        -*)
            usage "Unknown option '$1'"
            ;;
        *)
            file=$1
            ;;
    esac
    shift
done

if [ -z "$file" ] ; then
    usage "Not enough arguments"
fi

while read p; do
    ./getJson.sh -m $p
    sleep $delay
    ./getJson.sh -l -m $p
    sleep $delay
done <$file
