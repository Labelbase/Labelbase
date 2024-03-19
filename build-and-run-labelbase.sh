#!/bin/bash

docker-compose down # make sure Labelbase is terminated.

# Check env vars first

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

# Check git next

LAST_GIT_COMMIT_FILE=".last_git_commit"

if [ -f "$LAST_GIT_COMMIT_FILE" ]; then
    LAST_COMMIT=$(cat "$LAST_GIT_COMMIT_FILE")
else
    LAST_COMMIT=""
fi

git fetch origin master

LATEST_COMMIT=$(git rev-parse origin/master)





if [ "$LATEST_COMMIT" != "$LAST_COMMIT" ]; then
    echo "New Labelbase updates found. Pulling latest changes from $LAST_COMMIT, then build and run."
    git pull origin master --no-rebase
    echo $LATEST_COMMIT > "$LAST_GIT_COMMIT_FILE"
    DOCKER_COMPOSE_COMMAND="up --build -d"
else
    echo "Running Labelbase $LAST_COMMIT."
    DOCKER_COMPOSE_COMMAND="up -d"
fi

docker-compose $DOCKER_COMPOSE_COMMAND
echo "Excecute 'docker-compose down' to terminate Labelbase."
