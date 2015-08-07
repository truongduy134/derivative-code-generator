"""
The module contains utility functions that related to sympy
"""

from sympy import diff, MatrixSymbol, Symbol
from sympy.concrete import summations
from sympy.matrices.expressions.matexpr import MatrixElement

def is_in_expr(expr, sympy_var):
    """ Checks if a sympy symbol or sympy matrix element is prenset in the
    input expression

    Args:
        expr : A sympy symbolic expression
        sympy_var : A sympy symbol or sympy matrix element

    Returns
        is_in : A boolean value indicating whether the sympy symbol or matrix
                element is present in the expression
    """
    tmp_symbol = sympy_var
    tmp_expr = expr
    if isinstance(sympy_var, MatrixElement):
        tmp_symbol = Symbol('__symbol_' + str(hash(sympy_var)))
        tmp_expr = expr.subs(sympy_var, tmp_symbol)
    return tmp_symbol in tmp_expr.free_symbols


def first_order_derivative(expr, first_var):
    """ Gets the first-order partial derivative of the given sympy expression
    Args:
        expr : A sympy symbolic expression
        first_var : A sympy symbol indicating the differentiation variable

    Returns:
        diff_expr : A sympy symbolic expression which is the first-order
                    partial derivative of the input expression
    """
    return diff(expr + 1, first_var)


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


def expand_expr(sympy_expr, deep=False):
    """ Expands the input sympy expression using sympy eval_sum_direct routine

    Args:
        sympy_expr : A sympy exression
        deep : A booealn value which is False by default. If it is True, all
               summation expressions are expanded. Otherwise, only the root
               expression is expanded if it is a summation expression

    Returns:
        expanded_expr : A sympy expression after doing summation expansion
    """
    old_args = sympy_expr.args
    new_args = old_args
    expr_func = sympy_expr.func
    expanded_expr = sympy_expr

    if sympy_expr.is_number or expr_func in [Symbol, MatrixSymbol]:
        deep = False

    if deep:
        if expr_func == MatrixElement:
            expanded_row_ind = expand_expr(old_args[1], deep)
            expanded_col_ind = expand_expr(old_args[2], deep)
            new_args = [old_args[0], expanded_row_ind, expanded_col_ind]
        elif expr_func == summations.Sum:
            new_args = [expand_expr(old_args[0], deep)] + list(old_args[1:])
        else:
            new_args = []
            for sub_expr in old_args:
                recurse_cond = not (sub_expr.is_number or
                                    sub_expr.func in [Symbol, MatrixSymbol])
                if recurse_cond:
                    new_args.append(expand_expr(sub_expr, deep))
                else:
                    new_args.append(sub_expr)
        expanded_expr = expr_func(*new_args)

    if expr_func == summations.Sum:
        expanded_expr = expanded_expr.args[0]
        limits = sympy_expr.args[1:]
        for limit in limits:
            expanded_expr = summations.eval_sum_direct(expanded_expr, limit)
    return expanded_expr
