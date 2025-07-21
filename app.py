from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from utils.parser import parser, lambda_parser
from utils.stream import Stream
import uuid
import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Configure PostgreSQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    ''
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define a model for storing results
class ExpressionResult(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    result = db.Column(db.String, nullable=True)
    error = db.Column(db.String, nullable=True)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Create a global stream for processing expressions
expression_stream = Stream()

# Function to process expressions in the background
def process_expression(item):
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.get_json()
    expr = data.get('expression', '')
    req_id = str(uuid.uuid4())
    expression_stream.add((expr, req_id))
    return jsonify({'request_id': req_id})

@app.route('/evaluate-lambda', methods=['POST'])
def evaluate_lambda():
    data = request.get_json()
    expr = data.get('expression', '')
    value = data.get('value', 0)  # User supplies a value for the lambda
    req_id = str(uuid.uuid4())
    # Add to stream with a tuple indicating lambda
    expression_stream.add(('lambda', expr, value, req_id))
    return jsonify({'request_id': req_id})

@app.route('/result/<req_id>', methods=['GET'])
def get_result(req_id):
    entry = db.session.get(ExpressionResult, req_id)
    if entry:
        result = {'result': entry.result} if entry.result else {'error': entry.error}
        db.session.delete(entry)
        db.session.commit()
        return jsonify(result)
    else:
        return jsonify({'status': 'processing'}), 202

if __name__ == '__main__':
    app.run(debug=True)