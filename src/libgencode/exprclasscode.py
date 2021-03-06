from abc import ABCMeta, abstractmethod

from .exprcode import JavaExprCodeGenerator
from .hessiancode import JavaHessianCodeGenerator
from .jacobiancode import JavaJacobianCodeGenerator

CODE_GENERATOR_VERSION = "0.0.1"
REPOSITORY_LINK = "https://github.com/truongduy134/derivative-code-generator"


class ExprClassCodeGenerator(object):
    """
    This is an abstract class for generating code to for a class containing
    functions to evaluate values of the input expression, to evaluate the
    Jacobian vector of the input expression, and to evaluate the Hessian matrix
    of the input expression.

    Public object member attributes:
        var_list : A list of Variable objects
        expr : A sympy symbolic expression
        config : A dictionary with key-value pairs indicating configuration for
                 code generation such as class name, package name, etc.
        diff_var_list : A list of Variable objects used for differentiation
                        when generating hessian and jacobian methods
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
            config=None,
            diff_var_list=None):
        """ Class constructor
        """
        self.var_list = var_list
        self.expr = sympy_expr
        if config is None:
            self.config = {}
            # By default, always generate code for computing Hessian matrix
            self.config["nohessian"] = False
        else:
            self.config = config
        if "classname" not in self.config:
            self.config["classname"] = ""
        if not self.config["classname"]:
            self.config["classname"] = ExprClassCodeGenerator.DEFAULT_CLASS_NAME

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
        if not self.config["nohessian"]:
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
            config=None,
            diff_var_list=None):
        """ Class constructor
        """
        ExprClassCodeGenerator.__init__(
            self, var_list, sympy_expr, config, diff_var_list)

    def _gen_code_header(self, file_handler):
        """ Generates Java code for the beginning section of a class file,
        such as class comments, package / file imports, etc. Class declaration
        should be generated by this method as well

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        # Header comment
        star_line = '*' * 78
        header_comment = (
            "/%s"
            "\n"
            " * Autogenerated by Derivative Code Generator (%s)\n"
            " *\n"
            " * More information at %s\n"
            " *\n"
            " * DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT "
            "YOU ARE DOING\n"
            " %s/"
            "\n\n"
        )
        file_handler.write(header_comment % (
            star_line,
            CODE_GENERATOR_VERSION,
            REPOSITORY_LINK,
            star_line
        ))

        # Package and class
        if ("package" in self.config) and self.config["package"]:
            file_handler.write("package %s;\n\n" % self.config["package"])
        file_handler.write("public class %s {\n" % self.config["classname"])

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
            modifier_list=["public", "static"])
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
            ["public", "static"],
            self.config["classname"])
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
            ["public", "static"],
            self.config["classname"])
        code_generator.gen_code(file_handler)

    def _gen_code_constructor(self, file_handler):
        """ Generates Java code for class constructor.

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        # Use implicit default class constructor
        return

    def default_file_name(self):
        """ Gets the default file name (with extension) for the source code file
        of this class.

        Returns:
            file_name : a string representing a file name with java extension.
        """
        return self.config["classname"] + "." + "java"
