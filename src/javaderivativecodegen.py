from derivativecodegen import (
    DerivativeCodeGenerator,
    first_order_derivative,
    second_order_derivative)
from javaexprcodegen import JavaExprCodeGenerator

class JavaDerivativeCodeGenerator(DerivativeCodeGenerator):
    """
    This is a class inherited from DerivativeCodeGenerator that generates
    Java code to compute partial derivatives for an input mathematical
    multivariate expression
    """

    def __init__(
            self,
            var_list,
            sympy_expr,
            base_func_name=None,
            tab_type=None,
            tab_size=None):
        """ Class constructor
        """
        DerivativeCodeGenerator.__init__(
            self, var_list, sympy_expr, base_func_name, tab_type, tab_size)

    def gen_code(
            self,
            file_handler,
            first_var_ind,
            second_var_ind=None,
            auto_add_suffix=True):
        """ Generates Java code for function to compute a partial derivative
        Args:
            file_handler : an output file handler to write the code to
            first_ind : an integer indicating the index of the first variable
                        for differentiation
            second_ind : an integer indicating the index of the second variable
                         for differentiation (maybe None if we compute
                         first-order derivative)
            auto_add_suffix : a boolean variable indicating a suffix should be
                added to method name. If it is false, method name is the
                same as self.base_func_name. If it is true, method name is 
                self.base_func_name followed by first_var_ind, and
                second_var_ind (if it is not None)
        """
        if second_var_ind is None:
            derivative_expr = first_order_derivative(
                self.expr, self._expanded_var_list[first_var_ind])
        else:
            derivative_expr = second_order_derivative(
                self.expr,
                self._expanded_var_list[first_var_ind],
                self._expanded_var_list[second_var_ind])
        func_name = self.get_derivative_func_name(
            first_var_ind, second_var_ind, auto_add_suffix)
        expr_generator = JavaExprCodeGenerator(
            self.var_list,
            derivative_expr,
            func_name,
            self.tab_type,
            self.tab_size)
        expr_generator.gen_code(file_handler)
