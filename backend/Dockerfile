FROM python:3.7-slim

ENV CONTAINER_HOME=/var/www

ADD . $CONTAINER_HOME
WORKDIR $CONTAINER_HOME

ARG DB_NAME
ENV DB_NAME $DB_NAME

RUN pip install -r $CONTAINER_HOME/requirements.txt
RUN python -m spacy download en_core_web_md