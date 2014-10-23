from sympy import diff
from hessiancodegen import HessianCodeGenerator
from exprcodegen import IndentType
from javaexprcodegen import JavaExprCodeGenerator

class JavaHessianCodeGenerator(HessianCodeGenerator):
    """
    This is a class inherited from HessianCodeGenerator that generates Java code
    to compute Hessian matrix for an input mathematical multivariate expression
    """

    def __init__(
            self,
            var_list,
            sympy_expr,
            func_name=None,
            tab_type=None,
            tab_size=None):
        """ Class constructor
        """
        HessianCodeGenerator.__init__(
            self, var_list, sympy_expr, func_name, tab_type, tab_size)

    def _gen_derivative_code(self, file_handler):
        """ Generates Java code for functions to compute partial derivatives of
        order 2 needed for Hessian matrix
        Args:
            file_handler : an output file handler to write the code to
        """
        num_var = len(self._expanded_var_list)
        for first in xrange(num_var):
            for second in xrange(first, num_var):
                derivative = diff(
                    diff(self.expr, self._expanded_var_list[second]) + 1,
                    self._expanded_var_list[first])
                expr_generator = JavaExprCodeGenerator(
                    self.var_list,
                    derivative,
                    self._get_derivative_func_name(first, second),
                    self.tab_type,
                    self.tab_size)
                expr_generator.gen_code(file_handler)

    def __gen_hessian_declaration(self, file_handler):
        """ Generates Java code for Hessian function declaration
        Args:
            file_handler : an output file handler to write the code to
        """
        header = "double[][] %s(" % self.func_name
        is_first = True
        for var in self.var_list:
            if is_first:
                is_first = False
            else:
                header += ", "
            dimension_size = len(var.dimension)
            type_decl = "double" + "[]" * dimension_size
            header += type_decl + " " + var.name
        header += ") {\n"
        file_handler.write(header)

    def _gen_hessian_code(self, file_handler):
        """ Generates Java code for functions to compute Hessian matrix
        Args:
            file_handler : an output file handler to write the code to
        """
        self.__gen_hessian_declaration(file_handler)
        # Function body
        num_var = len(self._expanded_var_list)
        param_list = ", ".join([var.name for var in self.var_list])
        temp_mat = "__temp"
        base_indent = "\t" if self.tab_type == IndentType.BY_TAB else (
            ' ' * self.tab_size)
        indent = base_indent

        file_handler.write((indent + "double[][] %s = new double[%d][%d];\n") %
            (temp_mat, num_var, num_var))
        for i in xrange(num_var):
            for j in xrange(i, num_var):
                file_handler.write((indent + "%s[%d][%d] = %s(%s);\n") % (
                    temp_mat, i, j, self._get_derivative_func_name(i, j),
                    param_list))
                if i == j:
                    continue
                file_handler.write((indent + "%s[%d][%d] = %s[%d][%d];\n") % (
                    temp_mat, j, i, temp_mat, i, j))
        file_handler.write((indent + "return %s;\n}\n") % temp_mat)
