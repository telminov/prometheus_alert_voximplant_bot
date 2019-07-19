# docker build -t prometheus_alert_voximplant_bot .

FROM python:3.7

RUN apt-get clean && apt-get update && apt-get install -y \
        vim curl supervisor \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED 1

ADD requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

COPY . /opt/app
WORKDIR /opt/app

RUN cp settings.sample.py settings.py

COPY supervisor/supervisord.conf /etc/supervisor/supervisord.conf
COPY supervisor/prod.conf /etc/supervisor/conf.d/app.conf

EXPOSE 8000
VOLUME /conf/

CMD test "$(ls /conf/settings.py)" || cp settings.sample.py /conf/settings.py; \
    rm settings.py;  ln -s /conf/settings.py settings.py; \
    touch /var/log/supervisor/webserver-stdout.log; \
    /usr/bin/supervisord -c /etc/supervisor/supervisord.conf; \
    tail -f /var/log/supervisor/webserver-stdout.log
