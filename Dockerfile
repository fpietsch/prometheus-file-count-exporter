FROM ubuntu:latest

LABEL maintainer "fabian pietsch "

RUN apt update -y && apt upgrade -y && apt-get install -y wget build-essential \ 
	&& apt-get install -y python python-distribute python-pip && rm -rf /var/cache/apt/*

RUN pip install prometheus_client --trusted-host pypi.python.org

RUN mkdir -pv /usr/local/bin && mkdir -pv /etc/ssl/certs && update-ca-certificates

ADD match_exporter.py /usr/local/bin/count_exporter.py

ADD config.txt /usr/local/bin/config.txt

ADD test.txt /tmp/test.txt

RUN chmod 0755 /usr/local/bin/count_exporter.py
RUN chmod 0755 /usr/local/bin/config.txt
RUN chmod 0755 /tmp/test.txt
EXPOSE 9666

ENTRYPOINT ["python", "/usr/local/bin/count_exporter.py"]
