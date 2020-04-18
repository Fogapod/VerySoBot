FROM python:alpine

WORKDIR /code

RUN apk add --no-cache --virtual build-deps \
		gcc \
		musl-dev && \
	apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
		keybase-client && \
	pip install discord.py pykeybasebot && \
	apk del build-deps

COPY entrypoint.sh .
COPY main.py .

RUN addgroup -S verysobot && \
	adduser -S verysobot -G verysobot && \
	chown -R verysobot:verysobot /code

USER verysobot

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "main.py"]

