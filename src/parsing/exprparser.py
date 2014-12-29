import sympy
from sympy import Symbol, MatrixSymbol, Matrix

import parsing.expryacc as expryacc

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
    program_lines = expryacc.parse(program_txt)
    print program_lines
    expr_str = ""
    var_list = []
    sympy_locals = {}

    for line in program_lines.split("\n"):
        if "var" in line:
            components = line.split()[1:]
            if len(components) > 1:
                if components[1] == "vector":
                    vector_size = int(components[2])
                    var_list.append(Variable(
                        components[0], VariableType.VECTOR, (vector_size,)))
                    sympy_locals[components[0]] = Matrix(
                        MatrixSymbol(components[0], vector_size, 1))
                if components[1] == "matrix":
                    num_rows = int(components[2])
                    num_cols = int(components[3])
                    var_list.append(Variable(
                        components[0], VariableType.MATRIX, (num_rows, num_cols)
                    ))
                    sympy_locals[components[0]] = Matrix(
                        MatrixSymbol(components[0], num_rows, num_cols))
            else:
                var_list.append(
                    Variable(components[0], VariableType.NUMBER, ()))
                sympy_locals[components[0]] = Symbol(components[0])
        elif "model" in line:
                components = line.split('=')
                expr_str = components[1]
        else:
            if "const" in line:
                components = line.split('=')
                expr_str = components[1]
                const_name = components[0].split()[1]
                expr_value = sympy.sympify(expr_str)
                if not is_const_expr(expr_value):
                    raise "Right hand-side is not a constant in constant declaration"
                sympy_locals[const_name] = expr_value

    sympy_expr = sympy.sympify(expr_str, sympy_locals)
    return (var_list, sympy_expr)
