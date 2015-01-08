from abc import ABCMeta, abstractmethod

import libgencode.codegenutil as codegenutil
from .exprcode import JavaExprCodeGenerator
from .hessiancode import JavaHessianCodeGenerator
from .jacobiancode import JavaJacobianCodeGenerator

class ExprClassCodeGenerator(object):
    """
    This is an abstract class for generating code to for a class containing
    functions to evaluate values of the input expression, to evaluate the
    Jacobian vector of the input expression, and to evaluate the Hessian matrix
    of the input expression.
    """

    __metaclass__ = ABCMeta

    DEFAULT_CLASS_NAME = "MathExpression"
    DEFAULT_EVAL_FUNC_NAME = "eval"
    DEFAULT_HESSIAN_FUNC_NAME = "hessian"
    DEFAULT_JACOBIAN_FUNC_NAME = "jacobian"

    def __init__(
            self,
            var_list,
            sympy_expr,
            class_name=None,
            diff_var_list=None):
        """ Class constructor
        """
        self.var_list = var_list
        self.expr = sympy_expr
        if class_name is None:
            self.class_name = ExprClassCodeGenerator.DEFAULT_CLASS_NAME
        else:
            self.class_name = class_name
        if diff_var_list is None:
            self.diff_var_list = self.var_list
        else:
            self.diff_var_list = diff_var_list

    @abstractmethod
    def _gen_code_header(self, file_handler):
        """ Generates code for the beginning section of a class file, such as
        class comments, package / file imports, etc. Class declaration should
        be generated by this method as well
        Subclass should implement this method to generate code in a specific
        programming language

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        pass

    @abstractmethod
    def _gen_code_footer(self, file_handler):
        """ Generates code for the ending section of a class file, such as
        adding closing bracket for class declaration
        Subclass should implement this method to generate code in a specific
        programming language

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        pass

    @abstractmethod
    def _gen_code_constructor(self, file_handler):
        """ Generates code for class constructor.
        Subclass should implement this method to generate code in a specific
        programming language

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        pass

    @abstractmethod
    def _gen_code_hessian(self, file_handler):
        """ Generates code for computing hessian matrix of the input expression
        Subclass should implement this method to generate code in a specific
        programming language

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        pass

    @abstractmethod
    def _gen_code_jacobian(self, file_handler):
        """ Generates code for computing jacobian of the input expression
        Subclass should implement this method to generate code in a specific
        programming language

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        pass

    @abstractmethod
    def _gen_code_eval(self, file_handler):
        """ Generates code for computing the input expression value
        Subclass should implement this method to generate code in a specific
        programming language

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        pass

    @abstractmethod
    def default_file_name(self):
        """ Gets the default file name (with extension) for the source code file
        of this class.
        Subclass should implement this method to return default file name with
        appropriate extension.

        Returns:
            file_name : a string representing a file name with extension.
        """
        pass

    def gen_code(self, file_handler):
        """ Generates code for the expression class
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        self._gen_code_header(file_handler)
        file_handler.tab()
        self._gen_code_constructor(file_handler)
        self._gen_code_eval(file_handler)
        self._gen_code_jacobian(file_handler)
        self._gen_code_hessian(file_handler)
        file_handler.untab()
        self._gen_code_footer(file_handler)

class JavaExprClassCodeGenerator(ExprClassCodeGenerator):
    """
    This is a class inherited from ExprClassCodeGenerator that generates
    Java code for a class containing functions to evaluate values of the input
    expression, to evaluate the Jacobian vector of the input expression, and to
    evaluate the Hessian matrix of the input expression.
    """

    def __init__(
            self,
            var_list,
            sympy_expr,
            class_name=None,
            diff_var_list=None):
        """ Class constructor
        """
        ExprClassCodeGenerator.__init__(
            self, var_list, sympy_expr, class_name, diff_var_list)

    def _gen_code_header(self, file_handler):
        """ Generates Java code for the beginning section of a class file,
        such as class comments, package / file imports, etc. Class declaration
        should be generated by this method as well

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        file_handler.write("public class %s {\n" % self.class_name)

    def _gen_code_footer(self, file_handler):
        """ Generates Java code for the ending section of a class file, such as
        adding closing bracket for class declaration

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        file_handler.write("}\n")

    def _gen_code_eval(self, file_handler):
        """ Generates Java code for computing the input expression value

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        code_generator = JavaExprCodeGenerator(
            self.var_list,
            self.expr,
            ExprClassCodeGenerator.DEFAULT_EVAL_FUNC_NAME,
            modifier_list=["public"])
        code_generator.gen_code(file_handler)

    def _gen_code_jacobian(self, file_handler):
        """ Generates Java code for computing jacobian of the input expression

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        code_generator = JavaJacobianCodeGenerator(
            self.var_list,
            self.expr,
            ExprClassCodeGenerator.DEFAULT_JACOBIAN_FUNC_NAME,
            self.diff_var_list,
            ["public"])
        code_generator.gen_code(file_handler)

    def _gen_code_hessian(self, file_handler):
        """ Generates Java code for computing hessian matrix of the input
        expression

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        code_generator = JavaHessianCodeGenerator(
            self.var_list,
            self.expr,
            ExprClassCodeGenerator.DEFAULT_HESSIAN_FUNC_NAME,
            self.diff_var_list,
            ["public"])
        code_generator.gen_code(file_handler)

    def _gen_code_constructor(self, file_handler):
        """ Generates Java code for class constructor.

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        file_handler.write(
            "%s {}\n\n" % codegenutil.get_java_func_declaration(
                self.class_name, "", [], ["public"]))

    def default_file_name(self):
        """ Gets the default file name (with extension) for the source code file
        of this class.

        Returns:
            file_name : a string representing a file name with java extension.
        """
        return self.class_name + "." + "java"
