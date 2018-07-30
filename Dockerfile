FROM alpine:latest

RUN apk add python3
RUN apk add py-pip

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY spectral-data ./spectral-data
COPY spectral-service ./spectral-service

CMD ["python", "./spectral-service/__init__.py"]