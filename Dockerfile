# ─ Etapa “base” ───────────────────────────────────────────
FROM python:3.10-alpine AS base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# nsjail y demás deps…
RUN apk add --no-cache nsjail libseccomp
COPY src/config/nsjail.cfg /etc/nsjail.cfg
RUN mkdir -p logs

COPY . .

ENV PYTHONPATH=/app/src
RUN pytest

# ─ Etapa “test” ───────────────────────────────────────────
FROM base AS test
# instala pytest (o, mejor, un requirements-dev.txt que incluya pytest, pytest-mock…)
RUN pip install --no-cache-dir pytest

# por defecto, al arrancar esta imagen ejecuta los tests
#ENTRYPOINT ["pytest", "--maxfail=1", "--disable-warnings", "-q"]
ENTRYPOINT ["python3", "main.py"]