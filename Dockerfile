# We're using Alpine Edge
FROM alpine:edge

#
# We have to uncomment Community repo for some packages
#
RUN sed -e 's;^#http\(.*\)/edge/community;http\1/edge/community;g' -i /etc/apk/repositories

# Installing Core Components
RUN apk add --no-cache --update \
    git \
    bash \
    python3 \
    sudo

RUN python3 -m ensurepip \
    && pip3 install --upgrade pip setuptools \
    && rm -r /usr/lib/python*/ensurepip && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache


#
# Install dependencies
#
RUN apk add --no-cache \
    py-pillow py-requests \
    py-sqlalchemy py-psycopg2 \
    libpq curl neofetch \
    musl py-tz py3-aiohttp \
    py-six py-click

RUN apk add --no-cache sqlite figlet

#
# Make user for userbot itself
#
RUN  sed -e 's;^# \(%wheel.*NOPASSWD.*\);\1;g' -i /etc/sudoers
RUN adduser userbot --disabled-password --home /home/userbot
RUN adduser userbot wheel

USER userbot
WORKDIR /home/userbot/userbot

#
# Install requirements
#
COPY ./requirementsDOCKER.txt /home/userbot/userbot
RUN sudo pip3 install -U pip
RUN sudo pip3 install -r requirementsDOCKER.txt

COPY ./ /home/userbot/userbot

#
# Copies session and config(if it exists)
#
# COPY ./userbot.session ./config.env /home/userbot/userbot/

RUN sudo chown -R userbot /home/userbot/userbot
RUN sudo chmod -R 777 /home/userbot/userbot
CMD ["python3","-m","userbot"]
