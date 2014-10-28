from abc import ABCMeta, abstractmethod
from sympy import Matrix, MatrixSymbol, Symbol, diff
from exprcodegen import VariableType, Variable

def first_order_derivative(expr, first_var):
    """ Gets the first-order partial derivative of the given sympy expression
    Args:
        expr : A sympy symbolic expression
        first_var : A sympy symbol indicating the differentiation variable

    Returns:
        diff_expr : A sympy symbolic expression which is the first-order
                    partial derivative of the input expression  
    """
    return diff(expr + 1, first_var)

def second_order_derivative(expr, first_var, second_var):
    """ Gets the second-order partial derivative of the given sympy expression
    Args:
        expr : A sympy symbolic expression
        first_var : A sympy symbol indicating the first differentiation variable
        second_var : A sympy symbol indicating the second differentiation
                     variable

    Returns:
        diff_expr : A sympy symbolic expression which is the second-order
                    partial derivative of the input expression  
    """
    return first_order_derivative(
        first_order_derivative(expr, first_var),
        second_var)

class DerivativeCodeGenerator(object):
    """
    This is an abstract class for generating code to compute partial derivative
    for an input mathematical multivariate expression

    Public object member attributes:
        var_list : A list of Variable objects
        expr : A sympy symbolic expression to be differentiated
        base_func_name : A string representing name (with possible suffices)
                         of the generated partial derivative method
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

    DEFAULT_BASE_FUNC_NAME = "partialDerivative"

    def __init__(
            self,
            var_list,
            sympy_expr,
            base_func_name=None,
            tab_type=None,
            tab_size=None):
        """ Class constructor
        """
        self.var_list = var_list
        self.expr = sympy_expr
        if base_func_name is None:
            self.base_func_name = DEFAULT_BASE_FUNC_NAME
        else:
            self.base_func_name = base_func_name
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

    def get_num_expanded_var(self):
        """ Returns the number of variables after expanding the variable list
        """
        return len(self._expanded_var_list)

    def get_derivative_func_name(
            self,
            first_var_ind,
            second_var_ind=None,
            auto_add_suffix=True):
        """ Gets the name for the function to compute the partial derivative
        Args:
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

        Returns:
            func_name : A string representing the derivative function name
        """
        if not auto_add_suffix:
            return self.base_func_name
        func_name = self.base_func_name + "_" + str(first_var_ind)
        if second_var_ind is not None:
            func_name += "_" + str(second_var_ind)
        return func_name

    @abstractmethod
    def gen_code(
            self,
            file_handler,
            first_var_ind,
            second_var_ind=None,
            auto_add_suffix=True):
        """ Generates code for function to compute a partial derivative
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
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
        pass

    def gen_code_all_first_order(self, file_handler):
        """ Generates code for all first-order derivative functions. Note that
            for each derivative function, its name is self.base_func_name
            followed by the index of the variable used in differentiation
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        for var_ind in xrange(self.get_num_expanded_var()):
            self.gen_code(file_handler, var_ind, None, True)

    def gen_code_all_second_order(self, file_handler):
        """ Generates code for all second-order derivative functions. Note that
            for each derivative function, its name is self.base_func_name
            followed by indices of two variables used in differentiation
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        for first_var_ind in xrange(self.get_num_expanded_var()):
            for second_var_ind in xrange(self.get_num_expanded_var()):
                self.gen_code(file_handler, first_var_ind, second_var_ind, True)
