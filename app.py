from flask import Flask, request, jsonify, render_template
from parser import parser

app = Flask(__name__)

# Serve the HTML front end from templates/
@app.route('/')
def index():
    return render_template('index.html')

# Evaluate an expression sent in a POST request
@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.get_json()
    expr = data.get('expression', '')
    try:
        result = parser(expr)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)