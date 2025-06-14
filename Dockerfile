FROM ubuntu:22.04

# 1) Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 python3-pip git build-essential clang libpython3-dev pkg-config \
    protobuf-compiler libprotobuf-dev libseccomp-dev autoconf bison flex \
    libnl-3-dev libnl-route-3-dev libnl-genl-3-dev && rm -rf /var/lib/apt/lists/*

# 2) Copy application and configs
WORKDIR /app
# 2.1) Make src/ visible as top-level imports
ENV PYTHONPATH=/app/src
COPY . .

# 3) Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt \
    && mv src/nsjail.cfg /etc/nsjail.cfg \
    && mkdir -p logs

# 4) Build nsjail
RUN git clone --recursive https://github.com/google/nsjail.git /opt/nsjail \
    && cd /opt/nsjail && make && cp nsjail /usr/local/bin/

# 5) Expose and start
EXPOSE 8080
ENTRYPOINT ["python3", "main.py"]