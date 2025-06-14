# main.py

import os
import sys

# ─── 1) Ensure Python can import from src/ ─────────────────────────────
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR  = os.path.join(BASE_DIR, 'src')
sys.path.insert(0, SRC_DIR)

# ─── 2) Initialize logging BEFORE any Flask imports ────────────────────
from adapters.logging_manager import LoggingService

logging_service = LoggingService(
    config_path=os.path.join(SRC_DIR, 'config', 'logging.yaml')
)
request_logger = logging_service.request_logger
error_logger   = logging_service.error_logger
result_logger  = logging_service.result_logger

request_logger.info("Initializing application logging")

# ─── 3) Now import Flask and your API pieces ──────────────────────────
from flask import Flask, jsonify, request
from flask_restx import Api
from version import __version__
from adapters.http.execute import bp as execute_bp
from adapters.http.docs import execute_ns

# ─── 4) Create Flask app and RESTX Api ────────────────────────────────
app = Flask(__name__)

# Use major version in the URL prefix
version_major = __version__.split('.')[0]
api_prefix   = f'/api/v{version_major}'

api = Api(
    app,
    version=__version__,
    title='Dynamic Python Execution API',
    description='API for dynamic execution of Python scripts',
    doc=f'{api_prefix}/docs'   # Swagger UI at /api/vX/docs
)

# ─── 5) Register your namespaces & blueprints ─────────────────────────
api.add_namespace(execute_ns,     path=f'{api_prefix}/execute')
app.register_blueprint(execute_bp, url_prefix=api_prefix)

result_logger.info("API namespaces and blueprints registered")

# ─── 6) Log every request body as JSON ───────────────────────────────
@app.before_request
def log_request():
    """Log HTTP method, path, and JSON body (if any)."""
    request_logger.info(
        f"{request.method} {request.path} | body={request.get_json(silent=True)}"
    )

# ─── 7) Catch-all exception handler ───────────────────────────────────
@app.errorhandler(Exception)
def handle_unhandled_error(err):
    """Log the stack and return a generic 500 payload."""
    error_logger.exception("Unhandled exception")
    return {'message': str(err)}, 500

# ─── 8) Version endpoint ─────────────────────────────────────────────
@app.route(f'{api_prefix}/version', methods=['GET'])
def version():
    """Return current API version."""
    request_logger.info("GET /version")
    return jsonify(version=__version__), 200

# ─── 9) Run! ─────────────────────────────────────────────────────────
if __name__ == '__main__':
    request_logger.info("Starting Flask app on 0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080)