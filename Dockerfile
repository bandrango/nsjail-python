# Use minimal Alpine with Python 3.10
FROM python:3.10-alpine

# Install nsjail and its libseccomp runtime
RUN apk add --no-cache nsjail libseccomp

# Set working directory
WORKDIR /app

# Copy Python requirements and install them without cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your nsjail config into /etc so nsjail can find it
COPY src/nsjail.cfg /etc/nsjail.cfg

# Create logs folder for your app
RUN mkdir -p logs

# Copy the rest of your application code
COPY . .

# Expose API port and set entrypoint
EXPOSE 8080
ENTRYPOINT ["python3", "main.py"]