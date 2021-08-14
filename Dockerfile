# syntax=docker/dockerfile:1

FROM python:3.6-slim-buster

# # all commands start from this directory
WORKDIR /app/
# # copy all files from this folder to working directory (ignores files in .dockerignore)
COPY . . /app/

RUN apt-get -y update
RUN pip3 install -r compiled_requirements.txt

# set the start command
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app