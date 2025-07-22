from flask import Blueprint, request, jsonify, render_template
from models import db, ExpressionResult
from utils.parser import parser, lambda_parser
from utils.stream import Stream
from utils.validation import is_valid_expression, is_valid_lambda
import uuid

# Create a Blueprint for the main application
bp = Blueprint('main', __name__)

# Create a global stream for processing expressions
expression_stream = Stream()

# Function to process expressions in the background
def process_expression(item, app):
    """
    Background task to process an expression or lambda expression.

    Args:
        item: Tuple containing expression data.
    """
    with app.app_context():
        try:
            if isinstance(item, tuple) and item[0] == 'lambda':
                _, expr, value, req_id = item
                result = lambda_parser(expr, value)
            else:
                expr, req_id = item
                result = parser(expr)
            entry = ExpressionResult(id=req_id, result=str(result), error=None)
        except Exception as e:
            entry = ExpressionResult(id=req_id, result=None, error=str(e))
        db.session.merge(entry)
        db.session.commit()

# Set the stream to use the processing function
expression_stream.forEach(process_expression)

@bp.route('/')
def index():
    """Render the main web interface."""
    return render_template('index.html')

@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok'})

@bp.route('/evaluate', methods=['POST'])
def evaluate():
    """
    API endpoint to submit a standard mathematical expression for evaluation.

    Returns:
        JSON with request_id.
    """
    data = request.get_json()
    expr = data.get('expression', '')
    if not is_valid_expression(expr):
        return jsonify({'error': 'Invalid expression'}), 400
    req_id = str(uuid.uuid4())
    expression_stream.add((expr, req_id))
    return jsonify({'request_id': req_id})

@bp.route('/evaluate-lambda', methods=['POST'])
def evaluate_lambda():
    """
    API endpoint to submit a lambda expression and value for evaluation.

    Returns:
        JSON with request_id.
    """
    data = request.get_json()
    expr = data.get('expression', '')
    value = data.get('value', 0)
    if not is_valid_lambda(expr):
        return jsonify({'error': 'Invalid lambda expression'}), 400
    req_id = str(uuid.uuid4())    
    expression_stream.add(('lambda', expr, value, req_id))
    return jsonify({'request_id': req_id})

@bp.route('/result/<req_id>', methods=['GET'])
def get_result(req_id):
    """
    API endpoint to poll for the result of an evaluated expression.

    Args:
        req_id (str): The request ID.

    Returns:
        JSON with result or error, or status 'processing'.
    """
    entry = db.session.get(ExpressionResult, req_id)
    if entry:
        result = {'result': entry.result} if entry.result else {'error': entry.error}
        db.session.delete(entry)
        db.session.commit()
        return jsonify(result)
    else:
        return jsonify({'status': 'processing'}), 202