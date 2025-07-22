from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ExpressionResult(db.Model):
    """
    SQLAlchemy model for storing the result and error of an evaluated expression.

    Attributes:
        id (str): Unique request ID.
        result (str): Evaluation result.
        error (str): Error message, if any.
    """
    id = db.Column(db.String(36), primary_key=True)
    result = db.Column(db.String, nullable=True)
    error = db.Column(db.String, nullable=True)