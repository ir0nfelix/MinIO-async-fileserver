FROM python:3.7-alpine3.8

MAINTAINER Artem Sudoma <artem.sudoma@gmail.com>

RUN addgroup -S -g 777 django && adduser -D -S -G django -u 777 django

RUN apk -U upgrade && apk -U add ca-certificates alpine-sdk musl-dev gcc python3-dev libmagic \
    gettext openjpeg openjpeg-tools openjpeg-dev libjpeg-turbo \
    libjpeg-turbo-utils libjpeg-turbo-dev musl freetype freetype-dev \
    libwebp lcms2 tiff zlib zlib-dev && \
    update-ca-certificates

RUN mkdir -p /code && chown -R django /code
WORKDIR /code
ADD . /code/

RUN pip3 install -r requirements.txt

EXPOSE 5000
CMD ["python", "app.py"]
