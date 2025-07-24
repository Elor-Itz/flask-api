from flask_restx import Api
from routes import api_ns

api = Api(
    title="Expression Evaluator API",
    version="1.0",
    description="API documentation for the Expression Evaluator microservice.",
    doc="/docs"
)

api.add_namespace(api_ns)