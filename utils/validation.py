import re

def is_valid_expression(expr):
    """
    Validate a standard mathematical expression.

    Only allows digits, operators (+, -, *, /), parentheses, and spaces.
    Disallows consecutive operators.

    Args:
        expr (str): The expression to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    # Only allow valid characters
    if not re.match(r'^[\d+\-*/().\s]+$', expr):
        return False
    # Disallow consecutive operators (simple check)
    if re.search(r'[\+\-\*/]{2,}', expr):
        return False
    return True

def is_valid_variable_expression(expr):
    """
    Validate a variable math expression (e.g., 'x*2+1').

    Only allows x, digits, operators (+, -, *, /, ^), parentheses, and spaces.
    Disallows consecutive operators and 'import'.

    Args:
        expr (str): The expression to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    # Only allow x, digits, operators, parentheses, spaces, and ^
    if not re.match(r'^[x\d+\-*/().\s^]+$', expr):
        return False
    # Disallow consecutive operators (simple check)
    if re.search(r'[\+\-\*/^]{2,}', expr):
        return False
    if 'import' in expr:
        return False
    return True