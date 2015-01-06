import sympy
from sympy import Symbol, MatrixSymbol

import parsing.expryacc as expryacc
from .astdef import AstExprType

from common.vardef import VariableType, Variable

def is_const_expr(sympy_expr):
    """ Checks if a sympy expression has constant values (which can be a
    number, vector, or matrix).

    Args:
        sympy_expr : A sympy expression

    Returns:
        is_constant : A boolean value indicating whether the input expression
                      has constant value
    """
    if hasattr(sympy_expr, "is_constant"):
        is_constant = sympy_expr.is_constant()
    else:
        is_constant = not sympy_expr.is_symbolic()
    return is_constant

def parse_expr_specification(program_txt):
    """ Parses a program text that contains the specification of expression

    Args:
        program_txt : A string which is the whole expression specification
                      program

    Returns:
        var_expr_pair : A pair whose first element is a list of symbol variables
                        used by the expression, and second element is a sympy
                        expression object
    """
    const_list, symbol_list, ast_main_expr = expryacc.parse(program_txt)

    var_list = []
    sympy_locals = {}

    for constant in const_list:
        expr_value = sympy.sympify(constant.value.to_sympy_str())
        if not is_const_expr(expr_value):
            raise Exception(
                "Right hand-side is not a constant in constant declaration")
        sympy_locals[constant.name] = expr_value

    for symbol in symbol_list:
        if symbol.type_info.type == AstExprType.AST_NUMBER_SYMBOL:
            var_list.append(
                Variable(symbol.name, VariableType.NUMBER, ()))
            sympy_locals[symbol.name] = Symbol(symbol.name)
        elif symbol.type_info.type == AstExprType.AST_VECTOR_SYMBOL:
            vector_size = int(symbol.type_info.dimension[0])
            var_list.append(Variable(
                symbol.name, VariableType.VECTOR, (vector_size,)))
            sympy_locals[symbol.name] = MatrixSymbol(
                symbol.name, vector_size, 1)
        else:
            # Matrix case
            dimension = symbol.type_info.dimension
            num_rows = int(dimension[0])
            num_cols = int(dimension[1])
            var_list.append(Variable(
                symbol.name, VariableType.MATRIX, (num_rows, num_cols)
            ))
            sympy_locals[symbol.name] = MatrixSymbol(
                symbol.name, num_rows, num_cols)

    # Main expression
    expr_str = ast_main_expr.to_sympy_str()
    print expr_str
    sympy_expr = sympy.sympify(expr_str, sympy_locals)
    return (var_list, sympy_expr)
