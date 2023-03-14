docker build app -t qr-maker:latest
docker run -it -d --rm -p 7313:7313 --name QRMaker qr-maker:latest
