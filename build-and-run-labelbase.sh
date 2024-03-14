#!/bin/sh

# git pull origin ...

if [[ -z "${MYSQL_ROOT_PASSWORD}" ]]; then
  echo "Error: MYSQL_ROOT_PASSWORD environment variable is not set"
  exit 1
else
  export $MYSQL_ROOT_PASSWORD
fi

if [[ -z "${MYSQL_PASSWORD}" ]]; then
  echo "Error: MYSQL_PASSWORD environment variable is not set"
  exit 1
else
  export $MYSQL_PASSWORD
fi

docker-compose up --build
