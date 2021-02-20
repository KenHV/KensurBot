FROM kenhv/kensurbot:alpine

RUN git clone -b sql-extended https://github.com/4amparaboy/KensurBot /root/userbot
RUN chmod 777 /root/userbot
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /root/userbot/

EXPOSE 80 443

CMD ["python3","-m","userbot"]
