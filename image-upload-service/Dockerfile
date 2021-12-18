FROM python:latest

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip3 install gunicorn

ENV FLASK_APP=app

COPY . .

CMD  [ "celery", "-A", "server.celery", "worker", "--loglevel=INFO", "--pool=solo", "-O", "fair"]



#CMD ["python", "app.py"]
#CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8088", "app:app"]

