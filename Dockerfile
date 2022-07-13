FROM kenhv/kensurbot:debian

RUN set -ex \
    && git clone -b master https://github.com/KenHV/KensurBot /home/userbot \
    && chmod 777 /home/userbot

COPY ./config.env /home/userbot/

WORKDIR /home/userbot/

CMD ["python3", "-m", "userbot"]
