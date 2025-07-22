import re

def is_valid_expression(expr):
    """
    Validate a standard mathematical expression.

    Only allows digits, operators (+, -, *, /), parentheses, and spaces.

    Args:
        expr (str): The expression to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.match(r'^[\d+\-*/().\s]+$', expr))

def is_valid_lambda(expr):
    """
    Validate a lambda expression.

    Checks that the expression starts with 'lambda' and does not contain 'import'.

    Args:
        expr (str): The lambda expression to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return expr.strip().startswith('lambda') and 'import' not in expr