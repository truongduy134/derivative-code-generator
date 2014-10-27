from jacobiancodegen import JacobianCodeGenerator
from javaderivativecodegen import JavaDerivativeCodeGenerator
from exprcodegen import IndentType, VariableType

class JavaJacobianCodeGenerator(JacobianCodeGenerator):
    """
    This is a class inherited from JacobianCodeGenerator that generates Java
    code to compute Hessian matrix for an input mathematical multivariate
    expression
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
        JacobianCodeGenerator.__init__(
            self, var_list, sympy_expr, func_name, tab_type, tab_size)

    def _get_derivative_code_generator(self):
        """ Returns the derivative code generator in Java
        """
        return JavaDerivativeCodeGenerator(
            self.var_list,
            self.expr,
            JacobianCodeGenerator.DEFAULT_DERIVATIVE_NAME,
            self.tab_type,
            self.tab_size)

    def __gen_jacobian_declaration(self, file_handler):
        """ Generates Java code for Jacobian function declaration
        Args:
            file_handler : an output file handler to write the code to
        """
        param_str = ""
        is_first = True
        for var in self.var_list:
            if is_first:
                is_first = False
            else:
                param_str += ", "
            if var.var_type == VariableType.NUMBER:
                type_decl = "double"
            else:
                type_decl = "double" + "[]" * len(var.dimension)
            param_str += type_decl + " " + var.name
        header = "double[] %s(%s) {\n" % (self.func_name, param_str)
        file_handler.write(header)

    def _gen_jacobian_code(self, file_handler):
        """ Generates Java code for function to compute Jacobian vector
        Args:
            file_handler : an output file handler to write the code to
        """
        self.__gen_jacobian_declaration(file_handler)
        # Function body
        num_var = self._diff_code_generator.get_num_expanded_var()
        # Function body
        num_var = self._diff_code_generator.get_num_expanded_var()
        param_list = ", ".join([var.name for var in self.var_list])
        temp_vector = "__temp"
        base_indent = "\t" if self.tab_type == IndentType.BY_TAB else (
            ' ' * self.tab_size)
        indent = base_indent

        file_handler.write(indent + "double[] %s = new double[%d];\n" %
            (temp_vector, num_var))
        for i in xrange(num_var):
            file_handler.write(indent + "%s[%d] = %s(%s);\n" % (
                temp_vector, i,
                self._diff_code_generator.get_derivative_func_name(
                    i, None, True),
                param_list))
        file_handler.write((indent + "return %s;\n}\n") % temp_vector)
