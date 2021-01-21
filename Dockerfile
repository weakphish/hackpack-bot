FROM ubuntu:20.04

MAINTAINER John Allison "jeallis2@ncsu.edu"

RUN yes | apt-get update
RUN yes | apt-get install -y python3-pip python3-dev

COPY ./requirements.txt /requirements.txt

WORKDIR /

RUN pip3 install -r requirements.txt

COPY . /

ENTRYPOINT [ "python3" ]

CMD [ "main.py" ]


