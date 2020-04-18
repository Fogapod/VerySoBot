FROM python:alpine

WORKDIR /code

COPY requirements.txt .

RUN apk add --no-cache --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing \
                keybase-client && \
	apk add --no-cache --virtual build-deps \
		gcc \
		musl-dev && \
	pip install -r requirements.txt && \
	apk del build-deps

COPY . .

RUN addgroup -S verysobot && \
	adduser -S verysobot -G verysobot && \
	chown -R verysobot:verysobot /code

USER verysobot

ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "-m", "verysobot"]

