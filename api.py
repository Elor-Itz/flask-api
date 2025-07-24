from flask_restx import Api, Namespace, fields

# Create namespaces
health_ns = Namespace('health', description='Health check operations')
evaluation_ns = Namespace('evaluation', description='Expression evaluation operations')

# Models for Swagger docs
evaluate_model = evaluation_ns.model('Evaluate', {
    'expression': fields.String(required=True, description='Mathematical expression')
})

evaluate_variable_model = evaluation_ns.model('EvaluateVariable', {
    'expression': fields.String(required=True, description='Variable math expression'),
    'value': fields.Raw(required=True, description='Value for variable')
})

result_model = evaluation_ns.model('Result', {
    'status': fields.String(description='Processing status'),
    'result': fields.String(description='Evaluation result'),
    'error': fields.String(description='Error message'),    
})

api = Api(
    title="Expression Evaluator API",
    version="1.0",
    description="API documentation for the Expression Evaluator microservice.",
    doc="/docs"
)

api.add_namespace(evaluation_ns)
api.add_namespace(health_ns)