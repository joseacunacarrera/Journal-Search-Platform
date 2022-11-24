FROM python:3.10.7-slim-bullseye

WORKDIR /app

COPY app/. .

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "./app.py"]