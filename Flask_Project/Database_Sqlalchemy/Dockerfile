FROM python:3.8-slim-buster

WORKDIR /flask-app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /flask-app

WORKDIR /flask-app

RUN flask db init
RUN flask db migrate
RUN flask db upgrade

CMD ["python","run.py"]