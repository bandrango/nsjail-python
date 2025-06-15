# ─ Etapa “base” ───────────────────────────────────────────
FROM python:3.10-alpine AS base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apk add --no-cache nsjail libseccomp
COPY src/config/nsjail.cfg /etc/nsjail.cfg
RUN mkdir -p logs

COPY . .

ENV PYTHONPATH=/app/src
RUN pytest

FROM base AS test
RUN pip install --no-cache-dir pytest

ENTRYPOINT ["python3", "main.py"]