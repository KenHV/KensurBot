# We're using Alpine stable
FROM alpine:edge

#
# We have to uncomment Community repo for some packages
#
RUN sed -e 's;^#http\(.*\)/v3.9/community;http\1/v3.9/community;g' -i /etc/apk/repositories

# Installing Python
RUN apk add --no-cache --update \
    bash \
    build-base \
    bzip2-dev \
    chromium \
    chromium-chromedriver \
    curl \
    figlet \
    gcc \
    git \
    jpeg-dev \
    libffi-dev \
    libpq \
    libwebp-dev \
    libxml2 \
    libxml2-dev \
    libxslt-dev \
    linux-headers \
    musl \
    neofetch \
    openssl-dev \
    php-pgsql \
    postgresql \
    postgresql-client \
    postgresql-dev \
    py-lxml \
    py-pillow \
    py-pip \
    py-psycopg2 \
    py-requests \
    py-sqlalchemy \
    py-tz \
    py3-aiohttp \
    python-dev \
    python3 \
    python3-dev \
    readline-dev \
    sqlite \
    sqlite-dev \
    sudo \
    util-linux \
    zlib-dev

RUN pip3 install --upgrade pip setuptools

# Copy Python Requirements to /app

RUN  sed -e 's;^# \(%wheel.*NOPASSWD.*\);\1;g' -i /etc/sudoers
RUN adduser userbot --disabled-password --home /home/userbot
RUN adduser userbot wheel
USER userbot
RUN mkdir /home/userbot/userbot
RUN git clone -b sql-extended https://github.com/AvinashReddy3108/PaperplaneExtended /home/userbot/userbot
WORKDIR /home/userbot/userbot
ADD ./requirements.txt /home/userbot/userbot/requirements.txt

#
# Copies session and config(if it exists)
#
COPY ./sample_config.env ./userbot.session* ./config.env* /home/userbot/userbot/

#
# Install requirements
#
RUN sudo pip3 install -r requirements.txt
ADD . /home/userbot/userbot
RUN sudo chown -R userbot /home/userbot/userbot
RUN sudo chmod -R 777 /home/userbot/userbot
CMD ["python3","-m","userbot"]
