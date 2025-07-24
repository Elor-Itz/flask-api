from flask import Blueprint, request, jsonify, render_template
from flask_restx import Resource
from models import db, ExpressionResult
from utils.parser import parser, variable_parser
from utils.stream import Stream
from utils.validation import is_valid_expression, is_valid_variable_expression
import uuid

from api import evaluation_ns, health_ns, evaluate_model, evaluate_variable_model, result_model

# Create a Blueprint for the main application
bp = Blueprint('main', __name__)

# Create a global stream for processing expressions
expression_stream = Stream()

# Function to process expressions in the background
def process_expression(item, app):
    """
    Background task to process an expression or variable expression.

    Args:
        item: Tuple containing expression data.
    """
    with app.app_context():
        try:
            if isinstance(item, tuple) and item[0] == 'variable':
                _, expr, value, req_id = item                
                result = variable_parser(expr, value)
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

@health_ns.route('/')
class HealthResource(Resource):
    def get(self):
        """Health check endpoint"""
        return {'status': 'ok'}

@evaluation_ns.route('/expression')
class EvaluateResource(Resource):
    @evaluation_ns.expect(evaluate_model)
    def post(self):
        """Submit a standard mathematical expression for evaluation"""
        data = evaluation_ns.payload
        expr = data.get('expression', '')
        if not is_valid_expression(expr):
            return {'error': 'Invalid expression'}, 400
        req_id = str(uuid.uuid4())
        try:            
            parser(expr)
        except Exception as e:
            return {'error': str(e)}, 400
        expression_stream.add((expr, req_id))
        return {'request_id': req_id}

@evaluation_ns.route('/variable')
class EvaluateVariableResource(Resource):
    @evaluation_ns.expect(evaluate_variable_model)
    def post(self):
        """Submit a variable math expression and value for evaluation"""
        data = request.get_json()
        expr = data.get('expression', '')
        value = data.get('value', 0)
        if not is_valid_variable_expression(expr):
            return {'error': 'Invalid variable expression'}, 400
        req_id = str(uuid.uuid4())
        expression_stream.add(('variable', expr, value, req_id))
        return {'request_id': req_id}

@evaluation_ns.route('/result/<string:req_id>')
class ResultResource(Resource):
    @evaluation_ns.marshal_with(result_model)
    def get(self, req_id):
        """
        Poll for the result of an evaluated expression.

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
            return result, 200
        else:
            return {'status': 'processing'}, 202

# Export for api.py
__all__ = ['bp', 'process_expression', 'expression_stream']