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

    # An array containing singleton operator type
    SINGLETON_OP_TYPE = [NUMBER, MATRIX, SYMBOL]

class VariableType(object):
    """ An enum class for variable types (number, vector, or matrix)
    """
    NUMBER = 0
    VECTOR = 1
    MATRIX = 2

class Variable(object):
    """
    A class that encapsulates variable information

    Public object member attributes:
        name : A string representing name of a variable
        var_type : A VariableType enum value indicating variable type
        dimension : A tuple indicating dimension of a variable
    """

    def __init__(self, name, var_type, dimension):
        """ Class constructor
        """
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

def get_java_func_declaration(
        func_name,
        ret_type,
        var_list,
        modifier_list):
    """ Gets a string which is a function / method declaration in Java.
        For example, "double foo(double x, double y)"
    Args:
        func_name : A string which is a name of the method / function
        ret_type : A string which is a return type of the method / function
        var_list : A list of Variable objects which are method parameters
        modifier_list : A list of modifiers for the method / function (such as
                        static, private, public, etc.)
    """
    param_str = ""
    is_first = True
    for var in var_list:
        if is_first:
            is_first = False
        else:
            param_str += ", "
        if var.var_type == VariableType.NUMBER:
            type_decl = "double"
        else:
            type_decl = "double" + "[]" * len(var.dimension)
        param_str += type_decl + " " + var.name
    modifier_str = " ".join(modifier_list)
    if modifier_str:
        modifier_str += " "
    func_delc = "%s%s %s(%s)" % (modifier_str, ret_type, func_name, param_str)
    return func_delc
