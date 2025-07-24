from flask import Blueprint, request, jsonify, render_template
from flask_restx import Namespace, Resource, fields
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

# --- Web UI routes ---
@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

# --- REST API using Flask-RESTX ---
api_ns = Namespace('api', description='Expression evaluation operations')

# Models for Swagger docs
evaluate_model = api_ns.model('Evaluate', {
    'expression': fields.String(required=True, description='Mathematical expression')
})

evaluate_lambda_model = api_ns.model('EvaluateLambda', {
    'expression': fields.String(required=True, description='Lambda expression'),
    'value': fields.Raw(required=True, description='Value for lambda')
})

result_model = api_ns.model('Result', {
    'result': fields.String(description='Evaluation result'),
    'error': fields.String(description='Error message')
})

@api_ns.route('/health')
class HealthResource(Resource):
    def get(self):
        """Health check endpoint"""
        return {'status': 'ok'}

@api_ns.route('/evaluate')
class EvaluateResource(Resource):
    @api_ns.expect(evaluate_model)
    def post(self):
        """Submit a standard mathematical expression for evaluation"""
        data = api_ns.payload
        expr = data.get('expression', '')
        if not is_valid_expression(expr):
            return {'error': 'Invalid expression'}, 400
        req_id = str(uuid.uuid4())
        expression_stream.add((expr, req_id))
        return {'request_id': req_id}

@api_ns.route('/evaluate-lambda')
class EvaluateLambdaResource(Resource):
    @api_ns.expect(evaluate_lambda_model)
    def post(self):
        """Submit a lambda expression and value for evaluation"""
        data = api_ns.payload
        expr = data.get('expression', '')
        value = data.get('value', 0)
        if not is_valid_lambda(expr):
            return {'error': 'Invalid lambda expression'}, 400
        req_id = str(uuid.uuid4())
        expression_stream.add(('lambda', expr, value, req_id))
        return {'request_id': req_id}

@api_ns.route('/result/<string:req_id>')
class ResultResource(Resource):
    @api_ns.marshal_with(result_model, code=200, description='Result or error')
    def get(self, req_id):
        """Poll for the result of an evaluated expression"""
        entry = db.session.get(ExpressionResult, req_id)
        if entry:
            result = {'result': entry.result} if entry.result else {'error': entry.error}
            db.session.delete(entry)
            db.session.commit()
            return result
        else:
            api_ns.abort(202, status='processing')

# Export for api.py
__all__ = ['bp', 'process_expression', 'expression_stream', 'api_ns']