#!/bin/sh
set -e # exit on any non-zero status (error)

# this entrypoint script checks that all required setup is done
# if not done, does it
# and then proceeds to execute the main "command" for this container

if [ ! -x "pb" ]; then
  echo "go build"
  go mod tidy
  go build
fi

if [ ! -x "$(which tygo)" ]; then
  echo "go install tygo"
  go install github.com/gzuidhof/tygo@latest
fi

if [ ! -x "$(which modd)" ]; then
  echo "go install modd"
  go install github.com/cortesi/modd/cmd/modd@latest
fi

exec "$@"