import codegenutil
from jacobiancodegen import JacobianCodeGenerator
from javaderivativecodegen import JavaDerivativeCodeGenerator

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
            modifier_list=None):
        """ Class constructor
        """
        JacobianCodeGenerator.__init__(
            self, var_list, sympy_expr, func_name, modifier_list)

    def _get_derivative_code_generator(self):
        """ Returns the derivative code generator in Java
        """
        return JavaDerivativeCodeGenerator(
            self.var_list,
            self.expr,
            JacobianCodeGenerator.DEFAULT_DERIVATIVE_NAME,
            self.modifier_list)

    def __gen_jacobian_declaration(self, file_handler):
        """ Generates Java code for Jacobian function declaration
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        func_declaration = codegenutil.get_java_func_declaration(
            self.func_name, "double[]", self.var_list, self.modifier_list)
        file_handler.write(func_declaration + " {\n")

    def _gen_jacobian_code(self, file_handler):
        """ Generates Java code for function to compute Jacobian vector
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        self.__gen_jacobian_declaration(file_handler)
        # Function body
        num_var = self._diff_code_generator.get_num_expanded_var()
        # Function body
        num_var = self._diff_code_generator.get_num_expanded_var()
        param_list = ", ".join([var.name for var in self.var_list])
        temp_vector = "__temp"

        file_handler.tab()
        file_handler.write("double[] %s = new double[%d];\n" % (
            temp_vector, num_var))
        for i in xrange(num_var):
            file_handler.write("%s[%d] = %s(%s);\n" % (
                temp_vector, i,
                self._diff_code_generator.get_derivative_func_name(
                    i, None, True),
                param_list))
        file_handler.write("return %s;\n" % temp_vector)
        file_handler.untab()
        file_handler.write("}\n")
