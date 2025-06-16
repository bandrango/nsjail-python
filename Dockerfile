FROM python:3.10-alpine AS base
WORKDIR /app
RUN apk add --no-cache nsjail

COPY hello.py .
COPY nsjail.simple.cfg .

USER root

# Original entrypoint (restored)
ENTRYPOINT ["nsjail", \
            "-Mo", \
            "--config=/app/nsjail.simple.cfg", \
            "--", \
            "/usr/local/bin/python3", \
            "/app/hello.py"]