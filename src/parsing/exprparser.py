import sympy
from sympy import Symbol, MatrixSymbol

import parsing.expryacc as expryacc
from .astdef import AstExprType, AstSymbolFlag

from common import sympyutils
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
    const_list, symbol_list, ast_exprs = expryacc.parse(program_txt)

    var_list = []
    diff_var_list = []
    sympy_locals = {}

    for constant in const_list:
        expr_value = sympy.sympify(constant.value.to_sympy_str())
        if not sympyutils.is_const_expr(expr_value):
            raise Exception(
                "Right hand-side is not a constant in constant declaration")
        sympy_locals[constant.name] = expr_value

    for symbol in symbol_list:
        symbol_type = symbol.type_info.type
        if symbol_type == AstExprType.NUMBER:
            var_obj = Variable(symbol.name, VariableType.NUMBER, ())
            if symbol.flag != AstSymbolFlag.USED_IN_LOOP:
                sympy_obj = Symbol(symbol.name, real=True)
            else:
                sympy_obj = Symbol(symbol.name, integer=True)
        elif symbol_type == AstExprType.VECTOR:
            vector_size = symbol.type_info.dimension[0]
            if isinstance(vector_size, str):
                vector_size = sympy_locals[vector_size]
            var_obj = Variable(symbol.name, VariableType.VECTOR, (vector_size,))
            sympy_obj = MatrixSymbol(symbol.name, vector_size, 1)
        else:
            # Matrix case
            dimension = symbol.type_info.dimension
            num_rows = dimension[0]
            if isinstance(dimension[0], str):
                num_rows = sympy_locals[dimension[0]]
            num_cols = dimension[1]
            if isinstance(dimension[1], str):
                num_cols = sympy_locals[dimension[1]]
            var_obj = Variable(
                symbol.name, VariableType.MATRIX, (num_rows, num_cols)
            )
            sympy_obj = MatrixSymbol(symbol.name, num_rows, num_cols)
        if symbol.flag != AstSymbolFlag.USED_IN_LOOP:
            var_list.append(var_obj)
            if symbol.flag == AstSymbolFlag.NORMAL:
                diff_var_list.append(var_obj)
        sympy_locals[symbol.name] = sympy_obj

    # Create reserved variables for loop iteration
    reserved_names = sympyutils.get_reserved_var_names()
    for var_name in reserved_names:
        sympy_locals[var_name] = Symbol(var_name, integer=True)

    # Sympify all expressions until we encounter main expression
    # Expressions declared after main expression are ignored
    for (expr_name, ast_expr) in ast_exprs:
        expr_str = ast_expr.to_sympy_str()
        raw_sympy_expr = sympy.sympify(expr_str, sympy_locals)
        try:
            sympy_expr = sympy.simplify(raw_sympy_expr)
        except:
            # If expr cannot be simplified due to errors, just take the original
            sympy_expr = raw_sympy_expr
        sympy_locals[expr_name] = sympy_expr
        if expr_name == "main":
            print expr_str
            break

    # Return Main expression
    return (var_list, diff_var_list, sympy_locals["main"])
