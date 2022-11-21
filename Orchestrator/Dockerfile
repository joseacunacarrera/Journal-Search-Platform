FROM python:3.10.7-slim-bullseye

WORKDIR /app

COPY app/. .
RUN apt-get update -y
RUN apt-get install -y curl

RUN curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | bash
RUN apt-get update -y

RUN apt install -y libmariadb3 libmariadb-dev

RUN apt install -y build-essential
RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "./app.py"]