#!/bin/bash

# waiting for db
echo "Waiting for test db"
expensemgr/docker/wait-for-db.sh

# creating db and running migrations
expensemgr/docker/application-testing/create-db.sh

# poetry run pytest ./tests