import os
import sys
import logging

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SRC_DIR  = os.path.join(BASE_DIR, 'src')
sys.path.insert(0, SRC_DIR)

from utils.config_loader import AppConfigLoader

config_loader = AppConfigLoader()
request_logger = logging.getLogger("request_logger")
error_logger = logging.getLogger("error_logger")
result_logger = logging.getLogger("result_logger")

flask_config = config_loader.get_flask_config()

request_logger.info("Initializing application logging")

from flask import Flask, jsonify, request
from flask_restx import Api
from version import __version__
from adapters.http.execute import bp as execute_bp
from adapters.http.docs import execute_ns

app = Flask(__name__)
app.config.update(flask_config)

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

api.add_namespace(execute_ns,     path=f'{api_prefix}/execute')
app.register_blueprint(execute_bp, url_prefix=api_prefix)

result_logger.info("API namespaces and blueprints registered")

@app.before_request
def log_request():
    """Log HTTP method, path, and JSON body (if any)."""
    request_logger.info(
        f"{request.method} {request.path} | body={request.get_json(silent=True)}"
    )

@app.errorhandler(Exception)
def handle_unhandled_error(err):
    """Log the stack and return a generic 500 payload."""
    error_logger.exception("Unhandled exception")
    return {'message': str(err)}, 500

@app.route(f'{api_prefix}/version', methods=['GET'])
def version():
    """Return current API version."""
    request_logger.info("GET /version")
    return jsonify(version=__version__), 200

if __name__ == '__main__':
    request_logger.info("Starting Flask app on 0.0.0.0:8080")
    app.run(host=flask_config.get("host", "0.0.0.0"),
            port=flask_config.get("port", 8080),
            debug=flask_config.get("debug", False))