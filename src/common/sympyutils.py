"""
The module contains utility functions that related to sympy
"""

from sympy import diff, Symbol

def first_order_derivative(expr, first_var):
    """ Gets the first-order partial derivative of the given sympy expression
    Args:
        expr : A sympy symbolic expression
        first_var : A sympy symbol indicating the differentiation variable

    Returns:
        diff_expr : A sympy symbolic expression which is the first-order
                    partial derivative of the input expression
    """
    # Check whether we should expand the expression
    tmp_symbol = Symbol('__symbol_' + str(hash(first_var)))
    tmp_expr = expr.subs(first_var, tmp_symbol)
    diff_expr = expr
    if tmp_symbol not in tmp_expr.free_symbols:
        diff_expr = expr.doit()

    return diff(diff_expr + 1, first_var)

def second_order_derivative(expr, first_var, second_var):
    """ Gets the second-order partial derivative of the given sympy expression
    Args:
        expr : A sympy symbolic expression
        first_var : A sympy symbol indicating the first differentiation variable
        second_var : A sympy symbol indicating the second differentiation
                     variable

    Returns:
        diff_expr : A sympy symbolic expression which is the second-order
                    partial derivative of the input expression
    """
    return first_order_derivative(
        first_order_derivative(expr, first_var),
        second_var)

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

def distinguish_dummy_vars(sympy_expr):
    """ Changes the names of dummy variables in the input sympy expression so
    that all dummy variables (usually used in sum or product loop) are
    guaranteed to have distinct names

    Args:
        sympy_expr : A sympy exression. The expression will be modified
    """
    atoms = sympy_expr.atoms()
    suffix = 0
    for atom in atoms:
        if atom.is_Dummy:
            atom.name += str(suffix)
            suffix += 1

def get_reserved_var_names():
    """ Gets the list of reserved variable names by the code generator (which
    may be used for temporary loop counters)

    Returns:
        var_names : A list of strings indicated reserved variable names
    """
    return ["___tmp_loop_counter_1", "___tmp_loop_counter_2"]
