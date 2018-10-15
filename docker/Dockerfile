FROM python:alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apk --no-cache add make gcc musl-dev linux-headers alpine-sdk pcre-dev

COPY Makefile /usr/src/app/
COPY requirements.txt /usr/src/app/
RUN make install

RUN apk del gcc musl-dev linux-headers alpine-sdk

RUN addgroup www-data && \
    adduser -D -G www-data www-data

COPY . /usr/src/app

EXPOSE 5000

CMD [ "uwsgi", "uwsgi.ini" ]
