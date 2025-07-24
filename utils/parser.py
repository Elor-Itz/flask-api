from abc import ABC
from abc import ABC,abstractmethod
import re

class Expression(ABC):
    @abstractmethod
    def calc(self) -> float:
        pass

class Num(Expression):
  def __init__(self, x: int):
    self.x = x  
  def calc(self)->int:
    return self.x

class BinExp(Expression):
  def __init__(self, left: Expression, right: Expression):
    self.left = left
    self.right = right  
 
class Plus(BinExp):
  def calc(self) -> float:
    return self.left.calc() + self.right.calc()

class Minus(BinExp):
  def calc(self) -> float:
    return self.left.calc() - self.right.calc()

class Mul(BinExp):
  def calc(self) -> float:
    return self.left.calc() * self.right.calc()

class Div(BinExp):
  def calc(self) -> float:
    return self.left.calc() / self.right.calc()

# Function to determine operator precedence
def precedence(op):
    """
    Return the precedence level of the given operator.

    Args:
        op (str): The operator ('+', '-', '*', '/', 'u+', 'u-').

    Returns:
        int: Precedence value (higher means higher precedence).
    """
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2, 'u+': 3, 'u-': 3}
    return precedence.get(op, 0)

# Parser function to evaluate normal expressions
def parser(expression) -> float:
    """
    Parse and evaluate a mathematical expression string.

    Args:
        expression (str): The mathematical expression to evaluate.

    Returns:
        float: The result of the evaluated expression.

    Raises:
        ValueError: If the expression is invalid.
    """   
    stack = []
    queue = []
    i = 0
    while i < len(expression):      
        token = expression[i]             

        # If character is a digit/number -> collect all digits and enqueue   
        if token.isdigit():        
            num = int(token)        
            i += 1
            # If a number
            while i < len(expression) and expression[i].isdigit():
                num = num * 10 + int(expression[i])
                i += 1
            queue.append(num)
            continue

        # If character is an operator
        elif token in '+-*/':
            # Handling unary operators
            if (token == '+' or token == '-') and (i == 0 or expression[i - 1] in '+-*/('):
                stack.append('u' + token)  # Mark as unary operator
            else:
                # If the operator takes precedence over the last in the stack -> pop and enqueue it
                while len(stack) > 0 and (stack[-1] in '+-*/' and (precedence(token) <= precedence(stack[-1]))):
                    queue.append(stack.pop())
                # We push the current operator to the stack anyway
                stack.append(token)             
        
        # If character is left parenthesis -> push onto the stack
        elif token == '(':
            stack.append(token)                      

        # If character is right parenthesis -> pop operators from stack and enqueue until the top one is a left parenthesis       
        elif token == ')':
            while stack and stack[-1] != '(':
              queue.append(stack.pop())          
            # Pop '('
            stack.pop()

        i += 1

    # While there are operators in the stack -> pop operators from stack and enqueue
    while len(stack) > 0:                               
        queue.append(stack.pop())            

    # Calculate result
    while len(queue) > 0:
        token = queue.pop(0)        
        
        # If a number -> pop and push onto the stack
        if isinstance(token, int) or (token[0] == '-' and token[1:].isdigit()):
          stack.append(token) 

        # If a unary operator -> pop the last operand; if '-' multiply operand by -1 and return to the stack
        elif stack and (token == 'u+' or token == 'u-'):
            op = stack.pop()
            if token == 'u-':
                stack.append(-op)

        # If a binary operator -> pop the last two operands from stack and push the performed operation
        elif stack and token in '+-*/':          
            right = stack.pop() 
            left = stack.pop()
            calc = 0
            if token == '+':              
                calc = left + right
            if token == '-': 
                calc = left - right                           
            if token == '*':
                calc = left * right
            if token == '/':
                calc = left / right
            stack.append(calc)            

    # print("{0} = {1}" .format(expression,stack[0]))    
    return stack[0]

# Parser function to evaluate variable expressions
def variable_parser(expression, value):
    """
    Safely evaluate a math expression with a variable 'x' using your custom parser.

    Args:
        expression (str): The math expression (e.g., 'x*2+1').
        value (float): The value to substitute for 'x'.

    Returns:
        float: The result of the evaluated expression.

    Raises:
        ValueError: If the expression is not valid or evaluation fails.
    """
    # Only allow x, digits, operators, parentheses, spaces
    if not re.match(r'^[x\d+\-*/().\s]+$', expression):
        raise ValueError("Unsafe characters in expression.")

    # Insert * for implicit multiplication (e.g., 2x -> 2*x)
    expr = re.sub(r'(\d)(x)', r'\1*\2', expression)
    expr = re.sub(r'(x)(\d)', r'\1*\2', expr)

    # Substitute x with value
    expr = expr.replace('x', str(value))

    # Validate consecutive operators
    if re.search(r'[\+\-\*/]{2,}', expr):
        raise ValueError("Invalid consecutive operators.")

    # Use your custom parser for evaluation
    try:
        result = parser(expr)
        return result
    except Exception as e:
        raise ValueError(f"Invalid math expression: {e}")
        