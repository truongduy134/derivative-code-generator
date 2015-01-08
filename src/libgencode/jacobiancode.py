from abc import ABCMeta, abstractmethod

import libgencode.codegenutil as codegenutil
from .derivativecode import JavaDerivativeCodeGenerator

class JacobianCodeGenerator(object):
    """
    This is an abstract class for generating code to compute Jacobian vector
    for an input mathematical multivariate expression

    Public object member attributes:
        var_list : A list of Variable objects
        expr : A sympy symbolic expression
        func_name : A string representing name of the generated Jacobian method
        diff_var_list : A list of Variable objects used in differentiation
        modifier_list : A list of strings indicating modifiers for the
                        jacobian method / function, and for derivative functions
                        (such as static, private, public, etc.)

    Protected object member attributes:
        _diff_code_generator : The code generator for partial derivatives
    """

    __metaclass__ = ABCMeta

    DEFAULT_FUNC_NAME = "jacobian"
    DEFAULT_DERIVATIVE_NAME = "partialDerivative"

    def __init__(
            self,
            var_list,
            sympy_expr,
            func_name=None,
            diff_var_list=None,
            modifier_list=None):
        """ Class constructor
        """
        self.var_list = var_list
        self.expr = sympy_expr
        if func_name is None:
            self.func_name = JacobianCodeGenerator.DEFAULT_FUNC_NAME
        else:
            self.func_name = func_name
        if diff_var_list is None:
            self.diff_var_list = self.var_list
        else:
            self.diff_var_list = diff_var_list
        if modifier_list is None:
            self.modifier_list = []
        else:
            self.modifier_list = modifier_list
        self._diff_code_generator = self._get_derivative_code_generator()

    @abstractmethod
    def _get_derivative_code_generator(self):
        """ Returns the derivative code generator
        Subclass should implement this method to get a derivative code generator
        in a specific programming language
        """
        pass

    @abstractmethod
    def _gen_jacobian_code(self, file_handler):
        """ Generates code for function to compute Jacobian vector
        Subclass should implement this method to generate function code in a
        specific programming language
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        pass

    def gen_code(self, file_handler):
        """ Generates code for a function to evaluate hessian matrix
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        self._diff_code_generator.gen_code_all_first_order(file_handler)
        self._gen_jacobian_code(file_handler)

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
            diff_var_list=None,
            modifier_list=None):
        """ Class constructor
        """
        JacobianCodeGenerator.__init__(
            self, var_list, sympy_expr, func_name,
            diff_var_list, modifier_list)

    def _get_derivative_code_generator(self):
        """ Returns the derivative code generator in Java
        """
        return JavaDerivativeCodeGenerator(
            self.var_list,
            self.expr,
            JacobianCodeGenerator.DEFAULT_DERIVATIVE_NAME,
            self.diff_var_list,
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
        num_diff_var = self._diff_code_generator.get_num_expanded_diff_var()
        param_list = ", ".join([var.name for var in self.var_list])
        temp_vector = "__temp"

        file_handler.tab()
        file_handler.write("double[] %s = new double[%d];\n" % (
            temp_vector, num_diff_var))
        for i in xrange(num_diff_var):
            file_handler.write("%s[%d] = %s(%s);\n" % (
                temp_vector, i,
                self._diff_code_generator.get_derivative_func_name(
                    i, None, True),
                param_list))
        file_handler.write("return %s;\n" % temp_vector)
        file_handler.untab()
        file_handler.write("}\n")
