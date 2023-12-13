FROM python:3.10-slim-bullseye

ENV PYTHONUNBUFFERED True

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

# CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app

#Modifying so that the program doesn't shut down. Hopefully this isn't too expensive. 
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app