from abc import ABCMeta, abstractmethod

class HessianCodeGenerator(object):
    """
    This is an abstract class for generating code to compute Hessian matrix
    for an input mathematical multivariate expression

    Public object member attributes:
        var_list : A list of Variable objects
        expr : A sympy symbolic expression
        func_name : A string representing name of the generated Hessian method
        tab_type : An IndentType enum indicating the generated code should be
                   indented by tab or space
        tab_size : A integer indicating the tab size. The value is ignored if
                   indentation type is TAB

    Protected object member attributes:
        _diff_code_generator : The code generator for partial derivatives
    """

    __metaclass__ = ABCMeta

    DEFAULT_FUNC_NAME = "hessian"
    DEFAULT_DERIVATIVE_NAME = "partialDerivative"

    def __init__(
            self,
            var_list,
            sympy_expr,
            func_name=None):
        """ Class constructor
        """
        self.var_list = var_list
        self.expr = sympy_expr
        if func_name is None:
            self.func_name = HessianCodeGenerator.DEFAULT_FUNC_NAME
        else:
            self.func_name = func_name
        self._diff_code_generator = self._get_derivative_code_generator()

    @abstractmethod
    def _get_derivative_code_generator(self):
        """ Returns the derivative code generator
        Subclass should implement this method to get a derivative code generator
        in a specific programming language
        """
        pass

    @abstractmethod
    def _gen_hessian_code(self, file_handler):
        """ Generates code for function to compute Hessian matrix
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
        self._diff_code_generator.gen_code_all_second_order(file_handler)
        self._gen_hessian_code(file_handler)
