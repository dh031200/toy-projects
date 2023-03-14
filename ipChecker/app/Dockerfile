FROM ubuntu:22.04

EXPOSE 7312

RUN apt-get update && apt-get install -y python3 pip
RUN pip install flask
COPY app.py /
COPY app.sh /

CMD ["/bin/bash", "app.sh"]