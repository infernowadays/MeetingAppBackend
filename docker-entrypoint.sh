#!/bin/bash -
#===============================================================================
#
#          FILE: entrypoint.sh
#
#         USAGE: ./entrypoint.sh
#
#   DESCRIPTION:
#
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (),
#  ORGANIZATION:
#       CREATED: 10.05.2019 01:53
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

dockerize -wait tcp://$PG_HOST:$PG_PORT -timeout 60s -- python manage.py migrate

exec "$@"
