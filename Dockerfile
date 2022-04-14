FROM ubuntu:latest

RUN apt update && apt install -y python3-pip

COPY . /yousician
WORKDIR /yousician

RUN pip3 install -r requirements.txt

CMD python3 ./app.py

