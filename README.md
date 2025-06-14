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
7. [Development](#-development)  
8. [Contributing](#-contributing)  
9. [License](#-license)

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
   docker build -t nsjail-python:latest .
   ```

## 🔌 Configuration

- `nsjail.cfg`: Customize resource limits (CPU, memory, filesystem).  
- Environment variables (in `docker run` or Kubernetes manifest):  
  - `PORT` (default: `8080`)  
  - `TIME_LIMIT` (seconds per execution)  

## 💻 Usage

1. **Run container locally**:  
   ```bash
   docker run -p 8080:8080 nsjail-python:latest
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

## 🛠 Development

1. **Install dependencies**:  
   ```bash
   pip install -r requirements.txt
   ```  
2. **Run tests** (add testing framework of your choice):  
   ```bash
   pytest
   ```  
3. **Lint & Format**:  
   ```bash
   flake8 . && black .
   ```

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.  

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
