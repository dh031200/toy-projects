FROM ubuntu:22.04

EXPOSE 7313

RUN apt-get update && apt-get install -y python3 pip 
RUN pip install flask numpy qrcode[pil]
COPY app.py /
COPY app.sh /

CMD ["/bin/bash", "app.sh"]
