FROM python:3.8-slim-buster

WORKDIR /flask-app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

WORKDIR /flask-app/BlueprintApp_TodoList

RUN flask db init
RUN flask db migrate
RUN flask db upgrade

WORKDIR /flask-app

CMD ["python","run.py"]