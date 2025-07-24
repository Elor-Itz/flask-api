from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class ExpressionResult(db.Model):
    """
    SQLAlchemy model for storing the result and error of an evaluated expression.

    Attributes:
        id (str): Unique request ID.
        expression (str): The original mathematical expression submitted for evaluation.
        result (str): Evaluation result.
        timestamp (datetime): Timestamp of when the expression was evaluated.
    """
    id = db.Column(db.String(36), primary_key=True)
    expression = db.Column(db.String)
    result = db.Column(db.String, nullable=True)    
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))