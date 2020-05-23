#!/bin/sh

if [ "$1" = "pg-init" ]; then
    docker run --name sqlalchemy-orm-psql \
        -e POSTGRES_PASSWORD=pass \
        -e POSTGRES_USER=usr \
        -e POSTGRES_DB=sqlalchemy \
        -p 5432:5432 \
        -d postgres
        echo "USER: usr\nPASSWORD: pass\nDB: sqlalchemy"
        export USER="usr" \
               PASSWORD="pass" \
               DB="sqlalchemy"

elif [ "$1" = "pg-rm" ]; then
   docker rm sqlalchemy-orm-psql

elif [ "$1" = "pg-stop" ]; then
    #sudo netstat -anp | grep 5432
    docker stop sqlalchemy-orm-psql

elif [ "$1" = "local" ]; then
    export TWEETS_FILE="/home/ray/XCS224N/Assignment_5/XCS224N-A5/outputs/test_outputs.txt"
    sh run.sh pg-init && \
    python -m app

elif [ "$1" = "cleanup" ]; then
  docker stop sqlalchemy-orm-psql
  docker rm sqlalchemy-orm-psql

fi