from sympy import diff
from hessiancodegen import HessianCodeGenerator
from javaexprcodegen import JavaExprCodeGenerator
from javaderivativecodegen import JavaDerivativeCodeGenerator

class JavaHessianCodeGenerator(HessianCodeGenerator):
    """
    This is a class inherited from HessianCodeGenerator that generates Java code
    to compute Hessian matrix for an input mathematical multivariate expression
    """

    def __init__(
            self,
            var_list,
            sympy_expr,
            func_name=None):
        """ Class constructor
        """
        HessianCodeGenerator.__init__(self, var_list, sympy_expr, func_name)

    def _get_derivative_code_generator(self):
        """ Returns the derivative code generator in Java
        """
        return JavaDerivativeCodeGenerator(
            self.var_list,
            self.expr,
            HessianCodeGenerator.DEFAULT_DERIVATIVE_NAME)

    def __gen_hessian_declaration(self, file_handler):
        """ Generates Java code for Hessian function declaration
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
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
        """ Generates Java code for function to compute Hessian matrix
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        self.__gen_hessian_declaration(file_handler)
        # Function body
        num_var = self._diff_code_generator.get_num_expanded_var()
        param_list = ", ".join([var.name for var in self.var_list])
        temp_mat = "__temp"
        
        file_handler.tab()
        file_handler.write("double[][] %s = new double[%d][%d];\n" % (
            temp_mat, num_var, num_var))
        for i in xrange(num_var):
            for j in xrange(i, num_var):
                file_handler.write("%s[%d][%d] = %s(%s);\n" % (
                    temp_mat, i, j,
                    self._diff_code_generator.get_derivative_func_name(
                        i, j, True),
                    param_list))
                if i == j:
                    continue
                file_handler.write("%s[%d][%d] = %s[%d][%d];\n" % (
                    temp_mat, j, i, temp_mat, i, j))
        file_handler.write("return %s;\n" % temp_mat)
        file_handler.untab()
        file_handler.write("}\n")
