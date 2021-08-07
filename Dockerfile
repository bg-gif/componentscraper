# syntax=docker/dockerfile:1

FROM python

# # all commands start from this directory
WORKDIR /mnt/c/coding/Scraping/componentscraper
# # copy all files from this folder to working directory (ignores files in .dockerignore)
COPY . . /mnt/c/coding/Scraping/componentscraper/
COPY compiled_requirements.txt /mnt/c/coding/Scraping/componentscraper/

RUN apt-get -y update
RUN pip3 install -r compiled_requirements.txt

# set the start command
CMD [ "python3", "-m", "flask", "run" ]