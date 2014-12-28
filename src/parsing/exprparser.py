import sympy
from sympy import Symbol, MatrixSymbol, Matrix

import parsing.expryacc as expryacc

from common.vardef import VariableType, Variable

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
        else:
            if "model" in line:
                components = line.split('=')
                expr_str = components[1]
    sympy_expr = sympy.sympify(expr_str, sympy_locals)
    return (var_list, sympy_expr)
