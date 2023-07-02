#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

readonly cmd="$*"

: "${POSTGRES_HOST:=database}"
: "${POSTGRES_PORT:=5432}"

dockerize \
  -wait "tcp://${POSTGRES_HOST}:${POSTGRES_PORT}" \
  -timeout 90s

>&2 echo 'PostgreSQL is up - continuing...'

exec $cmd
