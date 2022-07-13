FROM kenhv/kensurbot:debian

RUN set -ex \
    && git clone -b staging https://github.com/KenHV/KensurBot /home/userbot \
    && chmod 777 /home/userbot

COPY ./docker-compose.yaml ./config.env* /home/userbot/

WORKDIR /home/userbot/

CMD ["python3", "-m", "userbot"]
