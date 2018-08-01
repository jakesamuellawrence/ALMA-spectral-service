FROM alpine:latest

RUN apk add python3
RUN apk add py-pip
RUN apk add python3-dev
RUN apk add build-base libffi-dev openssl-dev

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --upgrade pip setuptools

RUN CC=gcc pip3 install astropy astroquery
RUN pip3 install --no-cache-dir -r requirements.txt

COPY spectral-data ./spectral-data
COPY spectral-service ./spectral-service

CMD ["python3", "./spectral-service/__init__.py"]