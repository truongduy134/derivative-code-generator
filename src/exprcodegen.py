from abc import ABCMeta, abstractmethod
from sympy import Add, Mul, Pow, Symbol, sin, cos, tan, cot
from sympy.matrices.expressions.matexpr import MatrixElement

class OperatorType(object):
    """ An enum class for different operator / operand types
    """
    UNKNOWN = 0
    NUMBER = 1
    SYMBOL = 2
    MATRIX = 3
    ADD_REAL = 4
    MUL_REAL = 5
    POW_REAL = 6
    SIN_REAL = 7
    COS_REAL = 8
    TAN_REAL = 9
    COT_REAL = 10

class IndentType(object):
    """ An enum class for identation types (by space or by tab)
    """
    BY_SPACE = 0
    BY_TAB = 1

class VariableType(object):
    """ An enum class for variable types (number, vector, or matrix)
    """
    NUMBER = 0
    VECTOR = 1
    MATRIX = 2

class Variable(object):
    """ A class that encapsulates variable information
    """
    # Class field
    name = ""
    var_type = VariableType.NUMBER
    dimension = ()

    def __init__(self, name, var_type, dimension):
        self.name = name
        self.var_type = var_type
        self.dimension = dimension

def get_operator_type(sympy_expr):
    """ Gets operator type of the root of the input expression tree

    Args:
        sympy_expr : A sympy symbolic expression (which can be treated as
                     a parse tree)

    Returns:
        op_type : a value of type OperatorType indicating the operation type
            of the root of the current parse tree 
    """
    if sympy_expr.is_number:
        return OperatorType.NUMBER

    operator = sympy_expr.func
    if operator == Add:
        return OperatorType.ADD_REAL
    if operator == Mul:
        return OperatorType.MUL_REAL
    if operator == Pow:
        return OperatorType.POW_REAL
    if operator == Symbol:
        return OperatorType.SYMBOL
    if operator == MatrixElement:
        return OperatorType.MATRIX
    if operator == sin:
        return OperatorType.SIN_REAL
    if operator == cos:
        return OperatorType.COS_REAL
    if operator == tan:
        return OperatorType.TAN_REAL
    if operator == cot:
        return OperatorType.COT_REAL
    return OperatorType.UNKNOWN

class ExprCodeGenerator(object):
    """
    This is an abstract class for generating code for an input
    mathematical expression
    """

    __metaclass__ = ABCMeta

    DEFAULT_TAB_SIZE = 2
    DEFAULT_TEMP_NAME = "__temp"
    DEFAULT_FUNC_NAME = "evaluate"

    # Class field
    tab_type = IndentType.BY_SPACE
    tab_size = DEFAULT_TAB_SIZE     # Used in case tab type is space
    expr = ""   # A sympy math expression
    _var_dict = {}
    var_list = []
    temp_var_prefix = DEFAULT_TEMP_NAME
    func_name = DEFAULT_FUNC_NAME
    __num_temp_var_used = 0

    def __init__(
            self,
            var_list,
            sympy_expr,
            func_name=None,
            tab_type=None,
            tab_size=None,
            temp_prefix=None):
        """ Class constructor
        """
        self.var_list = var_list
        self.expr = sympy_expr
        if func_name is None:
            self.func_name = ExprCodeGenerator.DEFAULT_FUNC_NAME
        else:
            self.func_name = func_name
        if temp_prefix is None:
            self.temp_var_prefix = ExprCodeGenerator.DEFAULT_TEMP_NAME
        else:
            self.temp_var_prefix = temp_prefix
        self.tab_type = IndentType.BY_SPACE if tab_type is None else tab_type
        if tab_size is None:
            self.tab_size = ExprCodeGenerator.DEFAULT_TAB_SIZE
        else:
            self.tab_size = tab_size
        self.__num_temp_var_used = 0
        self._var_dict = {var_obj.name: var_obj for var_obj in self.var_list}

    def _get_nxt_temp_var_name(self):
        """ Gets the name that can be used for the next temporary variable.
        Returns:
            A string that can be used as the name for the next temporary
            variable declared during the code generation
        """
        next_name = self.temp_var_prefix + "_" + str(self.__num_temp_var_used)
        self.__num_temp_var_used += 1
        return next_name

    def _get_indent_string(self):
        """ Gets indentation string for a statement
        Returns:
            a string contains indentation characters
        """
        if self.tab_type == IndentType.BY_TAB:
            return "\t"
        return ' ' * self.tab_size

    @abstractmethod
    def _gen_func_declaration(self, file_handler):
        """ Generates code for function declaration
        Subclass should implement this method to generate function
        declaration (prototype) in a specific programming language
        Args:
            file_handler : an output file handler to write the code to
        """
        pass

    @abstractmethod
    def _gen_code_operator(
            self,
            op_type,
            operand_names,
            result_holder_name,
            file_handler):
        """ Generates code for operators
        Subclass should implement this method to generate code in a specific
        programming language
        Args:
            op_type : a variable of type OperatorType indicating operator type
            operand_names : a list of strings of operand names
            result_holder_name : a string for a variable name that holds the
                final result
            file_handler : an output file handler to write the code to
        Example:
            self._gen_code_operator(OperatorType.ADD_REAL, ['a', 'b', 'c'],
                'result', outfile) generates code for the statement
                result = a + b + c 
        """
        pass

    @abstractmethod
    def _gen_return_code(self, result_holder_name, file_handler):
        """ Generates code at the end of function (for returning results, etc.)
        Subclass should implement this method to generate code in a specific
        programming language
        Args:
            result_holder_name : a string for a variable name that holds the
                final result of the whole expression
            file_handler : an output file handler to write the code to
        """
        pass

    @abstractmethod
    def _gen_arr_access_code(self, var_obj, index_tuple):
        """ Generates code for array / matrix element access
        Subclass should implement this method to generate code in a specific
        programming language
        Args:
            var_obj : an object containing information about the 
                      array / matrix variable, such as name, type, dimension
            index_tuple : a tuple indicating the index of the element accessed
        Returns:
            A string representing the code to access array / matrix element
        """
        pass

    def _gen_code_expr(self, sympy_expr, file_handler):
        """ Generates code for a function to evaluate input expression
        Args:
            sympy_expr : a sympy expression that needs code generation
            file_handler : an output file handler to write the code to
        Returns:
            A string representing the name of the variable holding the final
            result when evaluting the expression
        Example:
            d = self._gen_code_expr(a + b * c, file_handler) generates code to
            compute the expression a + b * c; and d is the variable name such
            that d = a + b * c 
        """
        operands = sympy_expr.args
        expr_op_type = get_operator_type(sympy_expr)
        operand_names = []
        if expr_op_type in (
            [OperatorType.NUMBER, OperatorType.SYMBOL, OperatorType.MATRIX]):
            # For these special operator type (e.g. expr = 1, expr = v, 
            # expr = M), the operand is the expression itself
            operands = (sympy_expr,)
        
        for operand in operands:
            operand_type = get_operator_type(operand)
            if operand_type == OperatorType.NUMBER:
                operand_names.append(str(operand.evalf()))
            elif operand_type == OperatorType.SYMBOL:
                operand_names.append(str(operand))
            elif operand_type == OperatorType.MATRIX:
                var_name = operand.args[0].name
                index_tuple = operand.args[1:]
                operand_names.append(self._gen_arr_access_code(
                    self._var_dict[var_name], index_tuple))
            else:
                operand_names.append(
                    self._gen_code_expr(operand, file_handler))

        temp_var_name = self._get_nxt_temp_var_name()
        self._gen_code_operator(
            expr_op_type,
            operand_names,
            temp_var_name,
            file_handler)
        return temp_var_name

    def gen_code(self, file_handler):
        """ Generates code for a function to evaluate the input expression
        Args:
            file_handler : an output file handler to write the code to
        """
        self._gen_func_declaration(file_handler)
        final_var_name = self._gen_code_expr(self.expr, file_handler) 
        self._gen_return_code(final_var_name, file_handler) 
