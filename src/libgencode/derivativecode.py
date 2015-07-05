from abc import ABCMeta, abstractmethod
from sympy import Matrix, MatrixSymbol, Symbol

from common import sympyutils
from common.vardef import VariableType
from .exprcode import JavaExprCodeGenerator


class DerivativeCodeGenerator(object):
    """
    This is an abstract class for generating code to compute partial derivative
    for an input mathematical multivariate expression

    Public object member attributes:
        var_list : A list of Variable objects
        expr : A sympy symbolic expression to be differentiated
        base_func_name : A string representing name (with possible suffices)
                         of the generated partial derivative method
        diff_var_list : A list of Variable objects used for differentiation
        modifier_list : A list of strings indicating modifiers for the
                        derivative method / function (such as static, private,
                        public, etc.)

    Protected object member attributes:
        _expanded_diff_var_list : The expanded diff var list.
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
            diff_var_list=None,
            modifier_list=None):
        """ Class constructor
        """
        self.var_list = var_list
        self.expr = sympy_expr
        if base_func_name is None:
            self.base_func_name = DerivativeCodeGenerator.DEFAULT_BASE_FUNC_NAME
        else:
            self.base_func_name = base_func_name
        if diff_var_list is None:
            self.diff_var_list = self.var_list
        else:
            self.diff_var_list = diff_var_list
        if modifier_list is None:
            self.modifier_list = []
        else:
            self.modifier_list = modifier_list
        # Expand the diff_var_list (because it contains differentiation
        # variables) . For example, if v is a variable matrix of size
        # 1 x 3, we add v[0, 1], v[0, 2], v[0, 3] to the list. The hessian
        # matrix is based on variables in this expanded list
        self._expanded_diff_var_list = []
        for var_obj in self.diff_var_list:
            if var_obj.var_type == VariableType.NUMBER:
                # Single symbol case
                self._expanded_diff_var_list.append(
                    Symbol(var_obj.name, real=True))
            else:
                # Matrix case
                shape = var_obj.dimension
                if var_obj.var_type == VariableType.VECTOR:
                    shape = (shape[0], 1)
                var_mat = Matrix(MatrixSymbol(var_obj.name, shape[0], shape[1]))
                for i in xrange(shape[0]):
                    for j in xrange(shape[1]):
                        self._expanded_diff_var_list.append(var_mat[i, j])

    def get_num_expanded_diff_var(self):
        """ Returns the number of variables after expanding the variable list
        """
        return len(self._expanded_diff_var_list)

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
    def _get_expr_generator_class(self):
        """ Gets the code generator class for derivative expressions
        Subclass should implement this method to return appropriate code
        generator class for expressions which is then used to construct
        an instance to generate code for derivative expressions

        Returns:
            generator_class : a subclass of ExprCodeGenerator which is used to
                              construct code generator instances
        """
        pass

    def gen_code(
            self,
            file_handler,
            first_var_ind,
            second_var_ind=None,
            auto_add_suffix=True):
        """ Generates code for function to compute a partial derivative
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file
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
        if second_var_ind is None:
            derivative_expr = sympyutils.first_order_derivative(
                self.expr, self._expanded_diff_var_list[first_var_ind])
        else:
            derivative_expr = sympyutils.second_order_derivative(
                self.expr,
                self._expanded_diff_var_list[first_var_ind],
                self._expanded_diff_var_list[second_var_ind])
        func_name = self.get_derivative_func_name(
            first_var_ind, second_var_ind, auto_add_suffix)
        expr_generator = self._get_expr_generator_class()(
            self.var_list, derivative_expr, func_name, self.modifier_list)
        expr_generator.gen_code(file_handler)

    def gen_code_all_first_order(self, file_handler):
        """ Generates code for all first-order derivative functions. Note that
            for each derivative function, its name is self.base_func_name
            followed by the index of the variable used in differentiation
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        for var_ind in xrange(self.get_num_expanded_diff_var()):
            self.gen_code(file_handler, var_ind, None, True)

    def gen_code_all_second_order(self, file_handler):
        """ Generates code for all second-order derivative functions. Note that
            for each derivative function, its name is self.base_func_name
            followed by the two indices i, j of two variables used in
            differentiation where i <= j. Here we assume the symmetry of
            second-order derivatives
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        num_diff_var = self.get_num_expanded_diff_var()
        for first_var_ind in xrange(num_diff_var):
            first_order_diff = sympyutils.first_order_derivative(
                self.expr, self._expanded_diff_var_list[first_var_ind])
            for second_var_ind in xrange(first_var_ind, num_diff_var):
                func_name = self.get_derivative_func_name(
                    first_var_ind, second_var_ind, True)
                second_order_diff = sympyutils.first_order_derivative(
                    first_order_diff,
                    self._expanded_diff_var_list[second_var_ind]
                )
                expr_generator = self._get_expr_generator_class()(
                    self.var_list,
                    second_order_diff,
                    func_name,
                    self.modifier_list
                )
                expr_generator.gen_code(file_handler)


class JavaDerivativeCodeGenerator(DerivativeCodeGenerator):
    """
    This is a class inherited from DerivativeCodeGenerator that generates
    Java code to compute partial derivatives for an input mathematical
    multivariate expression
    """

    def __init__(
            self,
            var_list,
            sympy_expr,
            base_func_name=None,
            diff_var_list=None,
            modifier_list=None):
        """ Class constructor
        """
        DerivativeCodeGenerator.__init__(
            self, var_list, sympy_expr, base_func_name,
            diff_var_list, modifier_list)

    def _get_expr_generator_class(self):
        """ Gets the Java code generator class for derivative expressions

        Returns:
            generator_class : The JavaExprCodeGenerator which is a subclass of
                              ExprCodeGenerator
        """
        return JavaExprCodeGenerator
