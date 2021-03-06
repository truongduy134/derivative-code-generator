import sympy

from sympy.matrices.expressions.matexpr import MatrixElement

from common.vardef import VariableType


class OperatorType(object):
    """ An enum class for different operator / operand types
    """
    (UNKNOWN,
     NUMBER,
     SYMBOL,
     MATRIX,
     EXTRACT_REAL,  # Get the real part of a complex number
     ABS_REAL,
     ADD_REAL,
     DIRAC_DELTA_REAL,
     MUL_REAL,
     POW_REAL,
     SIN_REAL,
     COS_REAL,
     TAN_REAL,
     COT_REAL,
     LOG_REAL,
     SIGN_REAL,
     SUM_LOOP,
     PRODUCT_LOOP,
     CUSTOM_FUNC) = range(19)

    # An array containing singleton operator type
    __SINGLETON_OP_TYPE = [NUMBER, MATRIX, SYMBOL]

    # Dictionary that maps Sympy operator / function classes to operator types
    __SYMPY_OPERATOR_TYPE_MAP = {
        MatrixElement: MATRIX,
        sympy.Abs: ABS_REAL,
        sympy.Add: ADD_REAL,
        sympy.cos: COS_REAL,
        sympy.cot: COT_REAL,
        sympy.DiracDelta: DIRAC_DELTA_REAL,
        sympy.log: LOG_REAL,
        sympy.Mul: MUL_REAL,
        sympy.Pow: POW_REAL,
        sympy.Product: PRODUCT_LOOP,
        sympy.re: EXTRACT_REAL,
        sympy.sign: SIGN_REAL,
        sympy.sin: SIN_REAL,
        sympy.Sum: SUM_LOOP,
        sympy.Symbol: SYMBOL,
        sympy.tan: TAN_REAL,
    }

    @staticmethod
    def is_singleton_op(op_code):
        """ Checks if the input operator code is of singleton type (i.e. it is
        special operator for a single number, or a symbol, or a matrix access)

        Args:
            op_code : an enum value defined in OperatorType class
        Returns:
            True if the input operator is of singleton type. False otherwise
        """
        return op_code in OperatorType.__SINGLETON_OP_TYPE

    @staticmethod
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
        if operator in OperatorType.__SYMPY_OPERATOR_TYPE_MAP:
            return OperatorType.__SYMPY_OPERATOR_TYPE_MAP[operator]
        if hasattr(operator, 'is_Function') and operator.is_Function:
            return OperatorType.CUSTOM_FUNC
        return OperatorType.UNKNOWN


class IndentType(object):
    """ An enum class for identation types (by space or by tab)
    """
    BY_SPACE = 0
    BY_TAB = 1


class FileCodeWriter(object):
    """ This class is a wrapper of normal file handler with writing mode.
        Instance of this class also takes care of code indentation when
        writing output code strings.

    Public object member attributes:
        file_name : Name of the file that is written to
        tab_type : An IndentType enum indicating the generated code should be
                   indented by tab key or space
        tab_size : A integer indicating the tab size. The value is ignored if
                   indentation type is BY_TAB (i.e. tab key)

    Private object member attributes:
        __file_handler : An output file handler to write the code to
        __num_tab_from_margin : Number of tabs from the left margin
        __indent_str : A string that contains indentation characters that is
                       a prefix to a code line
    """

    DEFAULT_TAB_SIZE = 2
    DEFAULT_TAB_TYPE = IndentType.BY_SPACE

    def __init__(
            self,
            file_name,
            tab_type=None,
            tab_size=None):
        if tab_type is None:
            self.tab_type = FileCodeWriter.DEFAULT_TAB_TYPE
        else:
            self.tab_type = tab_type
        if tab_size is None:
            self.tab_size = FileCodeWriter.DEFAULT_TAB_SIZE
        else:
            self.tab_size = tab_size
        self.file_name = file_name
        self.__num_tab_from_margin = 0
        self.__indent_str = self.__get_indent_string()
        self.__file_handler = None

    def __enter__(self):
        if not self.__file_handler:
            self.open()
            self.__file_handler.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__file_handler:
            self.__file_handler.__exit__(exc_type, exc_value, traceback)

    def open(self):
        """ Opens the file with specified file name for writing code
        """
        self.__file_handler = open(self.file_name, "w")

    def close(self):
        """ Closes the file
        """
        self.__file_handler.close()

    def tab(self):
        """ Increases the number of tabs from left margin by 1
        """
        self.__num_tab_from_margin += 1
        self.__indent_str = self.__get_indent_string()

    def untab(self):
        """ Decreases the number of tabs from left margin by 1 if possible
        """
        if self.__num_tab_from_margin > 0:
            self.__num_tab_from_margin -= 1
            self.__indent_str = self.__get_indent_string()

    def write(self, content_str):
        """ Writes a content string to a file handler with a proper prefix
            indentation string
        Args:
            content_str : A string representing the content
        """
        self.__file_handler.write(self.__indent_str + content_str)

    def __get_indent_string(self):
        """ Gets indentation string for a code line
        Returns:
            a string contains indentation characters
        """
        if self.tab_type == IndentType.BY_TAB:
            return '\t' * self.__num_tab_from_margin
        return ' ' * (self.__num_tab_from_margin * self.tab_size)


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

    Returns:
        A string that is the function / method declaration in Java
    """
    param_str = ""
    is_first = True
    for var in var_list:
        if is_first:
            is_first = False
        else:
            param_str += ", "
        type_decl = "double"
        if var.var_type == VariableType.VECTOR:
            type_decl += "[]"
        elif var.var_type == VariableType.MATRIX:
            type_decl += "[][]"
        param_str += type_decl + " " + var.name
    modifier_str = " ".join(modifier_list)
    if modifier_str:
        modifier_str += " "
    rettype_str = ret_type
    if rettype_str:
        rettype_str += " "
    func_delc = "%s%s%s(%s)" % (modifier_str, rettype_str, func_name, param_str)
    return func_delc
