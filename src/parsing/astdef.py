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
    (AST_NUMBER_SYMBOL
     AST_INT_SYMBOL
     AST_VECTOR_SYMBOL
     AST_MATRIX_SYMBOL) = range(4)

    def __init__(self, expr_type, dimension):
        """ Class constructor
        """
        self.type = expr_type
        self.dimension = dimension

    def is_single_member(self):
        """ Checks if the type represents a single member structure (e.g.
        a single number, a vector of size 1, a matrix of size 1 x 1)

        Returns:
            True if the type represents a single member structure.
            False otherwise
        """
        is_single = False
        if self.is_number_type():
            is_single = True
        elif self.type == AstExprType.AST_VECTOR_SYMBOL:
            if self.dimension[0] == 1:
                is_single = True
        else:
            if self.dimension[0] == 1 and self.dimension[1] == 1:
                is_single = True
        return is_single

<<<<<<< HEAD
    def is_size_one_mat_type(self):
        """ Checks if the type represents a matrix or vector of size 1

        Returns:
            True if the type represents a matrix or vector of size 1
            False otherwise
        """
        if self.is_number_type():
            return False
        return self.is_single_member()

    def is_number_type(self):
        """ Checks if the type represents a single real or integer number

        Returns:
            True if the type represents a single real or integer number.
            False otherwise
        """
        return (self.type in
                [AstExprType.AST_NUMBER_SYMBOL, AstExprType.AST_INT_SYMBOL])

class AstSymbolFlag(object):
    """
    An enum class that enumerates symbol flag values. For example, NO_DIFF
    means the symbol is not used as a differentiation variable, or USED_IN_LOOP
    means the symbol is a counter variable used in looping
    """
    (NORMAL,
     NO_DIFF,
     USED_IN_LOOP) = range(3)

class AstSymbol(object):
    """
    A class that encapsulates symbol variable information used in building the
    abstract syntax tree (AST)

    Public object member attributes:
        name : A string representing name of a symbol variable
        type_info : An instance of AstExprType indicating the variable type
        flag : A enum value of AstSymbolFlag indicating the usage of the symbol
    """

    def __init__(self, name, type_info, flag=None):
        """ Class constructor
        """
        self.name = name
        self.type_info = type_info
        if flag is None:
            self.flag = AstSymbolFlag.NORMAL
        else:
            self.flag = flag

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

    (SYMBOL,
     # Add, subtract, divide, multiply operations
     ADD,
     SUB,
     MUL,
     DIV,
     POW,
     UMINUS,            # Uniary minus
     # Functions
     SQRT,
     SIN,
     COS,
     TAN,
     COT,
     LN,
     # Distinct vector and matrix operations
     DOT,
     CROSS,
     TRANSPOSE,
     TRANSPOSE_SHORT,
     # Indexing
     INDEXING,
     # Looping
     RANGE,
     LOOP_SUM,
     LOOP_PRODUCT) = range(21)

    __dict_op_to_sympy_str = {
        ADD: "+",
        SUB: "-",
        MUL: "*",
        DIV: "/",
        POW: "**",
        UMINUS: "-",
        SQRT: "sqrt",
        SIN: "sin",
        COS: "cos",
        TAN: "tan",
        COT: "cot",
        LN: "log",
        TRANSPOSE: "Transpose"
    }
    __dict_str_to_binary_ops = {
        "+": ADD,
        "-": SUB,
        "*": MUL,
        "/": DIV,
        "^": POW,
        ".": DOT,
        "#": CROSS
    }
    __dict_str_to_func_ops = {
        "sqrt": SQRT,
        "sin": SIN,
        "cos": COS,
        "tan": TAN,
        "cot": COT,
        "ln": LN,
        "transpose": TRANSPOSE
    }
    __binary_ops = [ADD, SUB, MUL, DIV, POW, DOT, CROSS]
    __func_ops = [SQRT, SIN, COS, TAN, COT, LN, TRANSPOSE]

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
        available. For example, POW is represented by "**" in sympy.

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

    Protected object member attributes:
        _size_one_mat : A boolean flag indicating whether the true type is
                         is a vector / matrix of a single element. In our
                         expression language, all vectors / matrices of size 1
                         are treated as AST_NUMBER_SYMBOL. However, the
                         difference may matter when generating strings in other
                         languages (such as sympy)
    """

    def __init__(self, operator, operands, name=None):
        """ Class constructor
        """
        self.operator = operator
        self.operands = operands
        self._size_one_mat = False
        self.__set_expr_type()
        if name is None:
            self.name = ""
        else:
            self.name = name

    def __set_expr_type(self):
        """ Determines the type of the result of the expression.
        Updates expr_type and __size_one_mat attributes
        """
        if self.operator == AstOperator.SYMBOL:
            self.expr_type = self.operands[0].type_info
        elif self.operator == AstOperator.UMINUS:
            self.expr_type = self.operands[0].expr_type
        elif (self.operator == AstOperator.TRANSPOSE or
              self.operator == AstOperator.TRANSPOSE_SHORT):
            # Vector variables are column vectors. We treat row vectors
            # as matrix variables
            self.expr_type = AstExprType(
                AstExprType.AST_MATRIX_SYMBOL,
                self.operands[0].expr_type.dimension[::-1]
            )
        elif AstOperator.is_func_ops(self.operator):
            # Besides transpose, currently all other functions map 1 real
            # number to a real number
            self.expr_type = AstExprType(AstExprType.AST_NUMBER_SYMBOL, ())
        elif self.operator == AstOperator.AST_OP_DOT:
            self.expr_type = AstExprType(AstExprType.AST_NUMBER_SYMBOL, ())
        elif self.operator == AstOperator.INDEXING:
            self.expr_type = AstExprType(AstExprType.AST_NUMBER_SYMBOL, ())
        elif self.operator == AstOperator.MUL:
            # Hacking here
            if (self.operands[0].expr_type.is_number_type() and
                self.operands[1].expr_type.is_number_type()):
                self.expr_type = AstExprType(AstExprType.AST_NUMBER_SYMBOL, ())
            elif self.operands[0].expr_type.is_number_type():
                self.expr_type = self.operands[1].expr_type
            elif self.operands[1].expr_type.is_number_type():
                self.expr_type = self.operands[0].expr_type
            else:
                # Multiplication between vector and matrix
                new_dimension = (
                    self.operands[0].expr_type.dimension[0],
                    self.operands[1].expr_type.dimension[1]
                )
                self.expr_type = AstExprType(
                    AstExprType.AST_MATRIX_SYMBOL,
                    new_dimension
                )
        elif (self.operator == AstOperator.LOOP_SUM or
              self.operator == AstOperator.LOOP_PRODUCT):
            # Hacking here. For now, loop over only number
            self.expr_type = self.operands[0].expr_type
        elif self.operator == AstOperator.RANGE:
            self.expr_type = AstExprType(AstExprType.AST_VECTOR_SYMBOL, (2, 1))
        else:
            # Other binary operator
            self.expr_type = self.operands[0].expr_type
            if self.expr_type.is_number_type():
                self.expr_type = AstExprType(AstExprType.AST_NUMBER_SYMBOL, ())

        if self.is_size_one_mat_type():
            self.expr_type = AstExprType(AstExprType.AST_NUMBER_SYMBOL, ())
            self._size_one_mat = True

    def to_sympy_str(self):
        """ Returns a string of the expression following sympy syntax which can
        be evaluated using sympy.sympify function

        Returns:
            A sympy string of the expression
        """
        result_str = ""
        if self.operator == AstOperator.SYMBOL:
            result_str = self.operands[0].name
        elif self.operator == AstOperator.DOT:
            result_str = "((%s).T*(%s))[0,0]" % (
                self.operands[0].to_sympy_str(),
                self.operands[1].to_sympy_str()
            )
        elif self.operator == AstOperator.CROSS:
            result_str = "Matrix(%s).cross(Matrix(%s))" % (
                self.operands[0].to_sympy_str(),
                self.operands[1].to_sympy_str()
            )
        elif self.operator == AstOperator.UMINUS:
            result_str = "-(%s)" % self.operands[0].to_sympy_str()
        elif self.operator == AstOperator.INDEXING:
            index_strs = [operand.to_sympy_str()
                          for operand in self.operands[1:]]
            result_str = "(%s)[%s]" % (
                self.operands[0].to_sympy_str(),
                ','.join(index_strs)
            )
        elif self.operator == AstOperator.TRANSPOSE_SHORT:
            result_str = "(%s).T" % self.operands[0].to_sympy_str()
        elif AstOperator.is_func_ops(self.operator):
            operand_strs = [operand.to_sympy_str() for operand in self.operands]
            result_str = "%s(%s)" % (
                AstOperator.get_sympy_str(self.operator),
                ",".join(operand_strs)
            )
        elif self.operator == AstOperator.RANGE:
            result_str = "(%s,%s,%s)" % (
                self.operands[0].to_sympy_str(),
                self.operands[1].to_sympy_str(),
                self.operands[2].to_sympy_str()
            )
        elif (self.operator == AstOperator.LOOP_SUM or
              self.operator == AstOperator.LOOP_PRODUCT):
            sympy_func_str = "Sum"
            if self.operator == AstOperator.LOOP_PRODUCT:
                sympy_func_str = "Product"
            result_str = "%s(%s)" % (
                sympy_func_str,
                ",".join([operand.to_sympy_str() for operand in self.operands])
            )
        else:
            # The rest of binary operators (+, -, /, *, etc.)
            result_str = "(%s)%s(%s)" % (
                self.operands[0].to_sympy_str(),
                AstOperator.get_sympy_str(self.operator),
                self.operands[1].to_sympy_str()
            )

        if self._size_one_mat:
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
