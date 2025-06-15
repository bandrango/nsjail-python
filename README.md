# nsjail-python

Secure, scalable microservice for executing arbitrary Python code in an isolated sandbox using [nsjail](https://github.com/google/nsjail).


## 🚀 Overview

`nsjail-python` empowers you to safely run untrusted Python scripts in a cloud-native environment. By leveraging Google’s `nsjail` for process isolation and resource control, it mitigates security risks while providing a simple REST API to execute `main()` functions in user-submitted code.

## 📋 Table of Contents

1. [Features](#-features)  
2. [Architecture](#-architecture)  
3. [Prerequisites](#-prerequisites)  
4. [Installation](#-installation)  
5. [Configuration](#-configuration)  
6. [Usage](#-usage)  
9. [Documentation](#-documentation)

## ✨ Features

- **Isolated Execution**: Uses `nsjail` to sandbox Python processes, enforcing strict CPU and memory limits.  
- **RESTful API**: Single endpoint (`POST /execute`) accepts JSON payloads and returns the `main()` function’s output.  
- **Error Handling**: Validates presence of `main()` and ensures returned values are JSON serializable.  
- **Containerized**: Docker-ready for seamless deployment on Cloud Run.
- **CI/CD Ready**: Preconfigured GitHub Actions workflow for linting and build checks.

## 🏗 Architecture (Hexagonal Architecture)

```plaintext
Client (--JSON script--) → Flask/FastAPI Service → nsjail ⛓️→ Python Interpreter → Response
```  
- **API Layer**: Handles HTTP requests, payload validation, and response formatting.  
- **Sandbox Layer**: Invokes `nsjail` to execute user code under controlled constraints.  
- **Execution Layer**: Runs the Python interpreter to call `main()` and captures output.

## 🔧 Prerequisites

- Docker ≥ 20.10  
- Python ≥ 3.9  
- `nsjail` binary included via Dockerfile  

## ⚙️ Installation

1. **Clone the repository**:  
   ```bash
   git clone https://github.com/bandrango/nsjail-python.git
   cd nsjail-python
   ```  
2. **Build Docker image**:  
   ```bash
   docker buildx build --platform linux/arm64 -t nsjail-flask-service:latest .
   ```

## 🔌 Configuration

All environment settings and runtime parameters are centralized in the `application.yaml` file.
This configuration file defines key aspects of the sandbox environment, such as:
- NSJail
- Logging
- Flask

- `nsjail.cfg`: Customize resource limits (CPU, memory, filesystem).  

This approach ensures consistency across environments and simplifies deployment and maintenance.


## 💻 Usage

1. **Run container locally**:  
   ```bash
   docker run --rm  --platform linux/arm64 --name nsjail-flask-service -p 10180:8080 nsjail-flask-service
   ```  
2. **Execute a script**:  
   ```bash
   curl -X POST http://localhost:8080/execute \
     -H "Content-Type: application/json" \
     -d '{"script": "def main(): return {\"message\": \"Hello from nsjail-python!\"}"}'
   ```  
3. **Response**:  
   ```json
   {
        "result": {
            "message": "Hello from nsjail-python!"
        },
        "stdout": ""
    }
   ```

## 📄 Documentation

The REST API is documented using **OpenAPI (Swagger)**.

Once the service is running, you can access the interactive Swagger UI at: {domain}/api/v1/docs
