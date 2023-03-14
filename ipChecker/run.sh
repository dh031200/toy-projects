docker build app -t ipchecker:latest
docker run -it -d --rm -p 7312:7312 --name ipchecker ipchecker:latest
