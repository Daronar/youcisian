#!/bin/sh
docker rm -f songs_db
docker rm -f yous-app
docker network rm yous-network
docker build -t yousician-app .
docker network create --subnet 172.20.0.0/16 yous-network
docker run -d --name songs_db --ip 172.20.0.10 --network yous-network mongo:4.4
docker run -d --name yous-app --ip 172.20.0.20 -p 80:80 -e DB_HOST='172.20.0.10' -e PATH_TO_DATA='./migrations/songs.json' --network yous-network yousician-app