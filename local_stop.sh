#!/bin/sh
docker rm -f songs_db
docker rm -f yous-app
docker network rm yous-network