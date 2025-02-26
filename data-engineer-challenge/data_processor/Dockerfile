FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN apk add --no-cache bash
RUN apk add --no-cache openjdk17-jre
RUN apk add --no-cache gcompat
ENV JAVA_HOME /usr/lib/jvm/default-jvm

COPY . .
