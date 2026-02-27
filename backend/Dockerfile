FROM python:3.9-alpine

ENV FLASK_APP=manage.py
ENV FLASK_CONFIG=production
ENV TZ="Asia/Shanghai"

RUN adduser -D ustc
USER ustc

WORKDIR /home/ustc

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com -r requirements.txt

COPY app app
COPY manage.py config.py boot.sh ./
COPY scores ./scores


# run-time configuration
EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
