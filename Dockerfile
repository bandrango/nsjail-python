# ─ Base stage ───────────────────────────────────────────────
FROM python:3.10-alpine AS base

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install NsJail and required system libraries
RUN apk add --no-cache nsjail libseccomp

# Copy NsJail configuration and prepare folders
COPY src/config/nsjail.cfg /etc/nsjail.cfg
RUN mkdir -p /app/logs /app/tmp

# Copy application source code
COPY . .

# Change ownership of files so that 'nobody' (UID 65534) has access
RUN chown -R 65534:65534 /app /etc/nsjail.cfg

# Set Python module path
ENV PYTHONPATH=/app/src

# ─ Optional test stage ──────────────────────────────────────
FROM base AS test
RUN pip install --no-cache-dir pytest
# You can remove this block if tests are already run in CI pipelines

# ─ Final stage ──────────────────────────────────────────────
FROM base AS final

# Use a non-root user (nobody:nogroup → 65534:65534)
USER 65534:65534

# Set working directory again for final image
WORKDIR /app

# Launch application (adjust if using Flask, FastAPI, etc.)
ENTRYPOINT ["python3", "main.py"]