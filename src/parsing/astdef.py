"""
The module contains definitions for structures used to construct the abstract
syntax tree of the expression specification grammar
"""

class AstProgram(object):
    """
    A class that encapsulates the expression specification program information

    Public object member attributes:
        const_list : A list of constants (instances of AstConstant) declared
        var_list : A list of symbol variables (instances of AstSymbol) declared
        main_expr : An instance of AstMainExpression representing the main
                    expression of the program
    """
    def __init__(self, const_list, var_list, main_expr):
        self.const_list = const_list
        self.var_list = var_list
        self.main_expr = main_expr

class AstExprType(object):
    """
    A class that encapsulates an expression type and the dimension of the
    type (which is necessary in case of vectors and matrices)

    Public object member attributes:
        type : An enum value indicating the expression type
        dimension : A tuple representing the dimension of the type.
                    Each dimension parameter can be an integer, or a string
                    indicating the name of an integer variable. For example,
                    the dimension of a matrix can be ('R', 3) which means the
                    matrix has size R x 3 where R is an integer symbol variable.
    """

    # Enum constants for different types
    AST_NUMBER_SYMBOL = 2
    AST_VECTOR_SYMBOL = 3
    AST_MATRIX_SYMBOL = 4

    def __init__(self, expr_type, dimension):
        """ Class constructor
        """
        self.type = expr_type
        self.dimension = dimension

    def is_single_member(self):
        """ Checks if the type representing a single member structure (e.g.
        a single number, a vector of size 1, a matrix of size 1 x 1)

        Returns:
            True if the type representing a single member structure.
            False otherwise
        """
        is_single = False
        if self.type == AstExprType.AST_NUMBER_SYMBOL:
            is_single = True
        elif self.type == AstExprType.AST_VECTOR_SYMBOL:
            if self.dimension[0] == 1:
                is_single = True
        else:
            if self.dimension[0] == 1 and self.dimension[1] == 1:
                is_single = True
        return is_single

class AstSymbol(object):
    """
    A class that encapsulates symbol variable information used in building the
    abstract syntax tree (AST)

    Public object member attributes:
        name : A string representing name of a symbol variable
        type_info : An instance of AstExprType indicating the variable type
    """

    def __init__(self, name, type_info):
        """ Class constructor
        """
        self.name = name
        self.type_info = type_info

class AstConstant(object):
    """
    A class the encapsulates constant information used in building the abstract
    syntax tree (AST)

    Public object member attributes:
        name : A string representing the name of the constant variable
        value : The value held by this constant variable, which can be a single
                number, a vector, a matrix, or an expression
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value

class AstOperator(object):
    """
    An enum class that enumerates all types of operators in expression tree.
    It also has several helper functions used in constructing the abstract
    syntax tree (AST)
    """

    AST_OP_SYMBOL = 0
    AST_OP_CONST_NUMBER = 1
    AST_OP_CONST_ARRAY = 2

    # Add, subtract, divide, multiply operations
    AST_OP_ADD = 3
    AST_OP_SUB = 4
    AST_OP_MUL = 5
    AST_OP_DIV = 6
    AST_OP_POW = 7
    AST_OP_UMINUS = 8       # Uniary minus

    # Functions
    AST_OP_SQRT = 9
    AST_OP_SIN = 10
    AST_OP_COS = 11
    AST_OP_TAN = 12
    AST_OP_COT = 13
    AST_OP_LN = 14

    # Distinct vector and matrix operations
    AST_OP_DOT = 15
    AST_OP_CROSS = 16
    AST_OP_TRANSPOSE = 17
    AST_OP_TRANSPOSE_SHORT = 18

    # Indexing
    AST_OP_INDEXING = 19

    __dict_op_to_sympy_str = {
        AST_OP_ADD: "+",
        AST_OP_SUB: "-",
        AST_OP_MUL: "*",
        AST_OP_DIV: "/",
        AST_OP_POW: "**",
        AST_OP_UMINUS: "-",
        AST_OP_SQRT: "sqrt",
        AST_OP_SIN: "sin",
        AST_OP_COS: "cos",
        AST_OP_TAN: "tan",
        AST_OP_COT: "cot",
        AST_OP_LN: "log",
        AST_OP_TRANSPOSE: "Transpose"
    }
    __dict_str_to_binary_ops = {
        "+": AST_OP_ADD,
        "-": AST_OP_SUB,
        "*": AST_OP_MUL,
        "/": AST_OP_DIV,
        "^": AST_OP_POW,
        ".": AST_OP_DOT,
        "#": AST_OP_CROSS
    }
    __dict_str_to_func_ops = {
        "sqrt": AST_OP_SQRT,
        "sin": AST_OP_SIN,
        "cos": AST_OP_COS,
        "tan": AST_OP_TAN,
        "cot": AST_OP_COT,
        "ln": AST_OP_LN,
        "transpose": AST_OP_TRANSPOSE
    }
    __binary_ops = [
        AST_OP_ADD, AST_OP_SUB, AST_OP_MUL, AST_OP_DIV, AST_OP_POW,
        AST_OP_DOT, AST_OP_CROSS
    ]
    __func_ops = [
        AST_OP_SQRT, AST_OP_SIN, AST_OP_COS, AST_OP_TAN, AST_OP_COT,
        AST_OP_LN, AST_OP_TRANSPOSE
    ]

    @staticmethod
    def is_func_ops(ast_op):
        """ Checks whether the input operator is of function type (such as
        sqrt, ln, sin, etc.)

        Args:
            ast_op : An enum value of AstOperator
        Returns:
            True if ast_op is of function type. False otherwise
        """
        return ast_op in AstOperator.__func_ops

    @staticmethod
    def get_sympy_str(ast_op):
        """ Returns the sympy string of the input operator if such string is
        available. For example, AST_OP_POW is represented by "**" in sympy.

        Args:
            ast_op : An enum value of AstOperator
        Returns:
            A string which is sympy representation of the input operator.
            Or None if such mapping is not supported by the function
        """
        if ast_op not in AstOperator.__dict_op_to_sympy_str:
            return None
        return AstOperator.__dict_op_to_sympy_str[ast_op]

    @staticmethod
    def get_func_op(op_str):
        """ Returns a function operator for a given string

        Args:
            op_str : A string representing the name of the function operator
        Returns:
            The corresponding enum value for the function operator. Or None if
            there is no mapping
        """
        if op_str not in AstOperator.__dict_str_to_func_ops:
            return None
        return AstOperator.__dict_str_to_func_ops[op_str]

    @staticmethod
    def get_binary_op(op_str):
        """ Returns a binary operator for a given string

        Args:
            op_str : A string representing the binary operator
        Returns:
            The corresponding enum value for the binary operator. Or None if
            there is no mapping
        """
        if op_str not in AstOperator.__dict_str_to_binary_ops:
            return None
        return AstOperator.__dict_str_to_binary_ops[op_str]

class AstExpression(object):
    """
    A class that encapsulates expression information used in building the
    abstract syntax tree (AST)

    Public object member attributes:
        operator : An instance of AstOperator indicating the type of operator
                   at the root of this expression tree
        operands : A list of instances representing operands
        expr_type : An instance of AstExprType indicating the evaluated type
                    of the whole expression
        name : A string representing name of an expression
    """

    def __init__(self, operator, operands, name=None):
        """ Class constructor
        """
        self.operator = operator
        self.operands = operands
        self.expr_type = self.__get_expr_type()
        if name is None:
            self.name = ""
        else:
            self.name = name

    def __get_expr_type(self):
        """ Gets the type of the result of the expression

        Returns:
            An instance of AstExprType indicating the type of the result of
            the expression
        """
        result_type = None
        if self.operator == AstOperator.AST_OP_SYMBOL:
            result_type = self.operands[0].type_info
        elif self.operator == AstOperator.AST_OP_UMINUS:
            result_type = self.operands[0].expr_type
        elif (self.operator == AstOperator.AST_OP_TRANSPOSE or
              self.operator == AstOperator.AST_OP_TRANSPOSE_SHORT):
            result_type = AstExprType(
                self.operands[0].expr_type.type,
                self.operands[0].expr_type.dimension[::-1]
            )
        elif AstOperator.is_func_ops(self.operator):
            # Besides transpose, currently all other functions map 1 real
            # number to a real number
            result_type = self.operands[0].expr_type
        elif self.operator == AstOperator.AST_OP_DOT:
            result_type = AstExprType(AstExprType.AST_NUMBER_SYMBOL, ())
        elif self.operator == AstOperator.AST_OP_INDEXING:
            result_type = AstExprType(AstExprType.AST_NUMBER_SYMBOL, ())
        elif self.operator == AstOperator.AST_OP_MUL:
            # Hacking here
            if (self.operands[0].expr_type.type ==
                    AstExprType.AST_NUMBER_SYMBOL):
                result_type = self.operands[1].expr_type
            elif (self.operands[1].expr_type.type ==
                  AstExprType.AST_NUMBER_SYMBOL):
                result_type = self.operands[0].expr_type
            else:
                # Multiplication between vector and matrix
                new_dimension = (
                    self.operands[0].expr_type.dimension[0],
                    self.operands[1].expr_type.dimension[1]
                )
                result_type = AstExprType(
                    AstExprType.AST_MATRIX_SYMBOL,
                    new_dimension
                )
        else:
            # Other binary operator
            result_type = self.operands[0].expr_type
        return result_type


    def to_sympy_str(self):
        """ Returns a string of the expression following sympy syntax which can
        be evaluated using sympy.sympify function

        Returns:
            A sympy string of the expression
        """
        result_str = ""
        if self.operator == AstOperator.AST_OP_SYMBOL:
            result_str = self.operands[0].name
        elif self.operator == AstOperator.AST_OP_DOT:
            result_str = "((%s).T*(%s))[0,0]" % (
                self.operands[0].to_sympy_str(),
                self.operands[1].to_sympy_str()
            )
        elif self.operator == AstOperator.AST_OP_CROSS:
            result_str = "(%s).cross(%s)" % (
                self.operands[0].to_sympy_str(),
                self.operands[1].to_sympy_str()
            )
        elif self.operator == AstOperator.AST_OP_UMINUS:
            result_str = "-(%s)" % self.operands[0].to_sympy_str()
        elif self.operator == AstOperator.AST_OP_INDEXING:
            index_strs = [operand.to_sympy_str()
                          for operand in self.operands[1:]]
            result_str = "(%s)[%s]" % (
                self.operands[0].get_sympy_str(),
                ','.join(index_strs)
            )
        elif self.operator == AstOperator.AST_OP_TRANSPOSE_SHORT:
            result_str = "(%s).T" % self.operands[0].to_sympy_str()
        elif AstOperator.is_func_ops(self.operator):
            operand_strs = [operand.to_sympy_str() for operand in self.operands]
            result_str = "%s(%s)" % (
                AstOperator.get_sympy_str(self.operator),
                ",".join(operand_strs)
            )
        else:
            # The rest of binary operators (+, -, /, *, etc.)
            result_str = "(%s)%s(%s)" % (
                self.operands[0].to_sympy_str(),
                AstOperator.get_sympy_str(self.operator),
                self.operands[1].to_sympy_str()
            )

        if (self.expr_type.type != AstExprType.AST_NUMBER_SYMBOL
                and self.expr_type.is_single_member()):
            result_str = "(%s)[0,0]" % result_str

        return result_str

class AstMainExpression(AstExpression):
    """
    A class that encapsulates information of the MAIN expression (the expression
    for which we generate evaluation code, hessian and jacobian code)

    Public object member attributes:
        op_type : An instance of AstOperatorType indicating the type of operator
                  at the root of this expression tree
        operands : A list of instances representing operands
        expr_type : An instance of AstExprType indicating the evaluated type
                    of the whole expression

        var_list : A list of variables the expression used in the expression
        diff_var_list : A list of variables used as differentiation variables
                        when generating Jacobian and Hessian code.
    """

    def __init__(self, op_type, operands, var_list, diff_var_list):
        AstExpression.__init__(self, op_type, operands, "main")
        self.var_list = var_list
        self.diff_var_list = diff_var_list
