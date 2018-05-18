FROM python:3.6.3-jessie

LABEL maintainer "Alexander Konyukov <alexander@konyukov.ru>"

# let the container know that there is no tty
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /opt/duty-board
WORKDIR /opt/duty-board

COPY requirements.txt ./
RUN pip3 install -r requirements.txt 

EXPOSE 9000
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:9000 --timeout 30 --workers=1 --log-level=info"


COPY . ./ 
CMD ["gunicorn", "main:app"]
