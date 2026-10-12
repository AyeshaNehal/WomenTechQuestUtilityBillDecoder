import ast
import operator
import math

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

ALLOWED_FUNCTIONS = {
    'abs': abs,
    'round': round,
    'max': max,
    'min': min,
    'sum': sum,
    'len': len,
    'int': int,
    'float': float,
    'math': math
}

def safe_eval(expr: str, context: dict) -> any:
    try:
        tree = ast.parse(expr, mode='eval').body
        return _eval_node(tree, context)
    except Exception as e:
        return f"Error evaluating expression: {e}"

def _eval_node(node, context):
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Name):
        if node.id in context:
            return context[node.id]
        elif node.id in ALLOWED_FUNCTIONS:
            return ALLOWED_FUNCTIONS[node.id]
        else:
            raise NameError(f"Name '{node.id}' is not allowed or defined.")
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left, context)
        right = _eval_node(node.right, context)
        if type(node.op) in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[type(node.op)](left, right)
        else:
            raise TypeError(f"Operator {type(node.op).__name__} is not allowed.")
    elif isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand, context)
        if type(node.op) in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[type(node.op)](operand)
        else:
            raise TypeError(f"Operator {type(node.op).__name__} is not allowed.")
    elif isinstance(node, ast.Call):
        func = _eval_node(node.func, context)
        args = [_eval_node(arg, context) for arg in node.args]
        return func(*args)
    elif isinstance(node, ast.Attribute):
        value = _eval_node(node.value, context)
        if value is math and hasattr(math, node.attr):
            return getattr(math, node.attr)
        raise AttributeError(f"Attribute access not allowed: {node.attr}")
    elif isinstance(node, ast.List):
        return [_eval_node(elt, context) for elt in node.elts]
    elif isinstance(node, ast.Subscript):
        value = _eval_node(node.value, context)
        slice_val = _eval_node(node.slice, context)
        try:
            return value[slice_val]
        except (KeyError, IndexError, TypeError) as e:
            raise type(e)(f"Subscript error: {e}")
    else:
        raise TypeError(f"Unsupported AST node type: {type(node).__name__}")
