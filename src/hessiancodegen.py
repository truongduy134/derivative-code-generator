from abc import ABCMeta, abstractmethod
from sympy import Matrix, MatrixSymbol, Symbol
from exprcodegen import IndentType, VariableType, Variable

class HessianCodeGenerator(object):
    """
    This is an abstract class for generating code to compute Hessian matrix
    for an input mathematical multivariate expression

    Public object member attributes:
        var_list : A list of Variable objects
        sympy_expr : A sympy symbolic expression
        func_name : A string representing name of the generated Hessian method
        tab_type : An IndentType enum indicating the generated code should be
                   indented by tab or space
        tab_size : A integer indicating the tab size. The value is ignored if
                   indentation type is TAB

    Protected object member attributes:
        _expanded_var_list : The expanded var list. 
            For example, if v is a variable matrix of size  1 x 3, we add 
            v[0, 1], v[0, 2], v[0, 3] to the list. The hessian matrix is based 
            on variables in this expanded list
    """

    __metaclass__ = ABCMeta

    DEFAULT_TAB_SIZE = 2
    DEFAULT_FUNC_NAME = "hessian"
    DEFAULT_DERIVATIVE_NAME = "partialDerivative"

    def __init__(
            self,
            var_list,
            sympy_expr,
            func_name=None,
            tab_type=None,
            tab_size=None):
        """ Class constructor
        """
        self.var_list = var_list
        self.expr = sympy_expr
        if func_name is None:
            self.func_name = HessianCodeGenerator.DEFAULT_FUNC_NAME
        else:
            self.func_name = func_name
        if tab_type is None:
            self.tab_type = IndentType.BY_SPACE
        else:
            self.tab_type = tab_type
        if tab_size is None:
            self.tab_size = HessianCodeGenerator.DEFAULT_TAB_SIZE
        else:
            self.tab_size = tab_size
        # Expand the var list. For example, if v is a variable matrix of size 
        # 1 x 3, we add v[0, 1], v[0, 2], v[0, 3] to the list. The hessian
        # matrix is based on variables in this expanded list
        self._expanded_var_list = []
        for var_obj in self.var_list:
            if var_obj.var_type == VariableType.NUMBER:
                # Single symbol case
                self._expanded_var_list.append(Symbol(var_obj.name))
            else:
                # Matrix case
                shape = var_obj.dimension
                if var_obj.var_type == VariableType.VECTOR:
                    shape = (shape[0], 1)
                var_mat = Matrix(MatrixSymbol(var_obj.name, shape[0], shape[1]))
                for i in xrange(shape[0]):
                    for j in xrange(shape[1]):
                        self._expanded_var_list.append(var_mat[i, j])

    def _get_derivative_func_name(self, first_ind, second_ind):
        """ Gets the name for the function to compute the second-order partial
        derivative function
        Args:
            first_ind : an integer indicating the index of the first variable
                        for differentiation
            second_ind : an integer indicating the index of the second variable
                         for differentiation
        """
        return (HessianCodeGenerator.DEFAULT_DERIVATIVE_NAME +
            "_" + str(first_ind) + "_" + str(second_ind))

    @abstractmethod
    def _gen_derivative_code(self, file_handler):
        """ Generates code for functions to compute partial derivatives of
        order 2 needed for Hessian matrix
        Subclass should implement this method to generate function code in a
        specific programming language
        Args:
            file_handler : an output file handler to write the code to
        """
        pass

    @abstractmethod
    def _gen_hessian_code(self, file_handler):
        """ Generates code for functions to compute Hessian matrix
        Subclass should implement this method to generate function code in a
        specific programming language
        Args:
            file_handler : an output file handler to write the code to
        """
        pass

    def gen_code(self, file_handler):
        """ Generates code for a function to evaluate hessian matrix
        Args:
            file_handler : an output file handler to write the code to
        """
        self._gen_derivative_code(file_handler)
        self._gen_hessian_code(file_handler)
