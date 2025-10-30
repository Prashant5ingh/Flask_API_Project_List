FROM python:3.8-slim-buster

WORKDIR /flask-todoapp

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /flask-todoapp

CMD ["python","app.py"]