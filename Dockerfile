FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY spectral-data ./spectral-data
COPY spectral-service ./spectral-service

CMD ["python", "./spectral-service/__init__.py"]