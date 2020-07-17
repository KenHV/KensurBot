FROM kenhv/kensurbot:alpine

RUN git clone -b sql-extended https://github.com/KenHV/KensurBot /root/userbot
RUN mkdir /root/userbot/bin/
RUN chmod 777 /root/userbot
WORKDIR /root/userbot/

CMD ["python3","-m","userbot"]
