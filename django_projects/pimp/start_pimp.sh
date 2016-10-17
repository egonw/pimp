#!/bin/bash

source ../../venv/bin/activate
set -a
source .env
set +a
./wait-for-it.sh -h ${PIMP_DATABASE_HOST} -p ${PIMP_DATABASE_PORT} -t 0
honcho -e .env -e initial-setup.env run python manage.py migrate
honcho -e .env -e initial-setup.env run python setupInitialUser.py
honcho -f Procfile.docker start
