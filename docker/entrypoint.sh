#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

readonly cmd="$*"

: "${POSTGRES_HOST:=database}"
: "${POSTGRES_PORT:=5432}"

# We need this line to make sure that this container is started after the one
# with PostgreSQL:
dockerize \
  -wait "tcp://${DJANGO_DATABASE_HOST}:${DJANGO_DATABASE_PORT}" \
  -timeout 90s

# It is also possible to wait for other services as well: Redis, Elastic,
# MongoDB, etc.
>&2 echo 'PostgreSQL is up - continuing...'

# Evaluating passed command (do not touch):
exec $cmd
