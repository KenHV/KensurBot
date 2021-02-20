FROM kenhv/kensurbot:alpine

RUN git clone -b sql-extended https://github.com/4amparaboy/KensurBot /root/userbot
RUN chmod 777 /root/userbot
WORKDIR /root/userbot/

EXPOSE 80 443

CMD ["python3","-m","userbot"]
