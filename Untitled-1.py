#!/usr/bin/env python3
import os
import io
import json
import ast
import tempfile
import importlib.util
import contextlib
import logging
from flask import Flask, request, jsonify

# ---------------------
# Configure logging
# ---------------------
logger = logging.getLogger('script_service')
logger.setLevel(logging.INFO)
# File handler
fh = logging.FileHandler('app.log')
fh.setLevel(logging.INFO)
# Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

# ---------------------
# Flask application
# ---------------------
app = Flask(__name__)

# Allowed modules in user code
ALLOWED_MODULES = {'os', 'pandas', 'numpy'}

# ---------------------
# Utility functions
# ---------------------

def validate_imports(source, name='<source>'):
    """Ensure only allowed imports are in the code."""
    try:
        tree = ast.parse(source, filename=name)
    except SyntaxError as e:
        raise ValueError(f"Syntax error: {e}")
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split('.')[0]
                if mod not in ALLOWED_MODULES:
                    raise ValueError(f"Import of module '{mod}' not allowed")
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or '').split('.')[0]
            if mod not in ALLOWED_MODULES:
                raise ValueError(f"Import from module '{mod}' not allowed")


def load_user_module(source, tmp_path=None):
    """Load and return a Python module from source code after import validation."""
    validate_imports(source)
    path = tmp_path or source
    spec = importlib.util.spec_from_file_location('user_module', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def execute_script(source):
    """
    Execute user-provided code (file path or snippet), returning a dict
    with keys 'result' and 'stdout'.
    Raises ValueError on invalid input or execution errors.
    """
    is_file = os.path.isfile(source)
    is_snippet = not is_file and 'def main' in source
    if not (is_file or is_snippet):
        raise ValueError('Input must be a .py file path or a code snippet including def main()')

    # Read or write snippet to temp file
    if is_file:
        try:
            with open(source, 'r') as f:
                code = f.read()
        except Exception as e:
            raise ValueError(f'Error reading file: {e}')
        tmp_path = None
    else:
        code = source
        tmp = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py')
        tmp.write(code)
        tmp.close()
        tmp_path = tmp.name

    # Load module
    try:
        module = load_user_module(code, tmp_path)
    except Exception as e:
        if tmp_path:
            os.unlink(tmp_path)
        raise ValueError(f'Error loading module: {e}')

    # Clean up temp file if used
    if tmp_path:
        try:
            os.unlink(tmp_path)
        except:
            pass

    # Ensure main
    if not hasattr(module, 'main') or not callable(module.main):
        raise ValueError('No function main() found')

    # Capture stdout
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            result = module.main()
    except Exception as e:
        raise ValueError(f'Error executing main(): {e}')
    stdout = buf.getvalue()

    # Validate JSON serializable
    try:
        json.dumps(result)
    except Exception:
        raise ValueError('Return of main() must be JSON serializable')

    return {'result': result, 'stdout': stdout}

# ---------------------
# Flask route
# ---------------------
@app.route('/execute', methods=['POST'])
def execute():
    data = request.get_json(force=True)
    if not data or 'script' not in data:
        logger.error('Missing "script" in request payload')
        return jsonify(error='Missing "script" field'), 400

    raw = data['script']
    logger.info('Received execution request')

    # Strip wrapping braces if present
    if isinstance(raw, str) and raw.strip().startswith('{') and raw.strip().endswith('}'):
        stripped = raw.strip()[1:-1]
        logger.info('Stripped outer braces from script')
        source = stripped
    else:
        source = raw

    try:
        output = execute_script(source)
        logger.info('Execution successful')
        return jsonify(output), 200
    except ValueError as ve:
        logger.error(f'Execution error: {ve}')
        return jsonify(error=str(ve)), 400
    except Exception as e:
        logger.exception('Unexpected server error')
        return jsonify(error='Internal server error'), 500

# ---------------------
# App entrypoint
# ---------------------
if __name__ == '__main__':
    logger.info('Starting Flask service on port 8080')
    app.run(host='0.0.0.0', port=8080)



docker buildx build --platform linux/arm64 -t nsjail-flask-service:latest .
docker run --rm -it --platform linux/arm64 --name nsjail-flask-service -p 10180:8080 nsjail-flask-service   
docker exec -it nsjail-flask-service bash