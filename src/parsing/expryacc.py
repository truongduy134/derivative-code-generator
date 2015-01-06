import ply.yacc as pyyacc
from .exprlex import tokens
from .astdef import (
    AstConstant,
    AstExpression,
    AstExprType,
    AstMainExpression,
    AstOperator,
    AstSymbol
)

precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "MUL", "DIV", "DOT"),
    ("left", "EXP", "CROSS"),
    ("left", "APOSTROPHE"),
    ("right", "UMINUS")
)

environment = {}        # Map a string which is a name of an atom to its type

def p_file_description(p):
    """
    file_description : list_const_declarations list_var_declarations expr_main_declaration
    """
    p[0] = (p[1], p[2], p[3])

def p_list_const_declarations(p):
    """
    list_const_declarations : const_declaration list_const_declarations
                            | empty
    """
    if len(p) == 2:
        p[0] = []
    else:
        p[0] = [p[1]] + p[2]

def p_const_declaration(p):
    """
    const_declaration : CONST ID EQUAL expression
    """
    p[0] = AstConstant(p[2], p[4])
    environment[p[2]] = p[4].expr_type

def p_list_var_declarations(p):
    """
    list_var_declarations : var_declaration list_var_declarations
                          | empty
    """
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_var_declaration(p):
    """
    var_declaration : NUMBER ID
                    | VECTOR ID LPAREN INTEGER RPAREN
                    | MATRIX ID LPAREN INTEGER COMMA INTEGER RPAREN
    """
    if len(p) == 3:
        p[0] = AstSymbol(
            p[2],
            AstExprType(AstExprType.AST_NUMBER_SYMBOL, ())
        )
    elif len(p) == 6:
        p[0] = AstSymbol(
            p[2],
            AstExprType(AstExprType.AST_VECTOR_SYMBOL, (p[4], 1))
        )
    else:
        p[0] = AstSymbol(
            p[2],
            AstExprType(AstExprType.AST_MATRIX_SYMBOL, (p[4], p[6]))
        )
    environment[p[0].name] = p[0].type_info

def p_expr_declaration(p):
    "expr_main_declaration : EXPR MAIN EQUAL expression"
    p[0] = AstMainExpression(p[4].operator, p[4].operands, [], [])

def p_expression(p):
    """
    expression : LPAREN expression RPAREN
               | expression PLUS expression
               | expression MINUS expression
               | expression MUL expression
               | expression DIV expression
               | expression DOT expression
               | expression EXP expression
               | expression CROSS expression
               | expression APOSTROPHE
               | MINUS expression %prec UMINUS
               | math_func_call
               | loop_expression
               | vector_index
               | matrix_index
               | atom
    """
    num_components = len(p)
    if num_components == 2:
        p[0] = p[1]
    elif num_components == 3:
        if p[1] == "-":
            # expression : -expression
            p[0] = AstExpression(AstOperator.AST_OP_UMINUS, [p[2]])
        else:
            # expression : expression' (matrix transpose)
            p[0] = AstExpression(
                AstOperator.AST_OP_TRANSPOSE_SHORT, [p[1]])
    elif p[1] == "(":
        # expression : (expression)
        p[0] = p[2]
    else:
        # Binary operator
        p[0] = AstExpression(AstOperator.get_binary_op(p[2]), [p[1], p[3]])

def p_loop_expression(p):
    """
    loop_expression : for_statements loop_func LPAREN expression RPAREN
    """
    op_type = AstOperator.AST_OP_LOOP_SUM
    if p[2] == "product":
        op_type = AstOperator.AST_OP_LOOP_PRODUCT
    p[0] = AstExpression(op_type, [p[4]] + p[1])

def p_for_statements(p):
    """
    for_statements : for_statement for_statements
                   | for_statement
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]

def p_for_statement(p):
    """
    for_statement : FOR ID IN integer_range
    """
    loop_symbol = AstSymbol(
        p[2],
        AstExprType(AstExprType.AST_NUMBER_SYMBOL, ())
    )
    p[0] = AstExpression(
        AstOperator.AST_OP_RANGE,
        [AstExpression(AstOperator.AST_OP_SYMBOL, [loop_symbol])] + p[4]
    )

def p_math_func_call(p):
    """
    math_func_call : math_func LPAREN expression RPAREN
    """
    p[0] = AstExpression(AstOperator.get_func_op(p[1]), [p[3]])

def p_matrix_index(p):
    """
    matrix_index : vector_index LSQRBRAC expression RSQRBRAC
    """
    operands = [p[1].operands[0], p[1].operands[1], p[3]]
    p[0] = AstExpression(AstOperator.AST_OP_INDEXING, operands)

def p_vector_index(p):
    """
    vector_index : ID LSQRBRAC expression RSQRBRAC
                 | LPAREN expression RPAREN LSQRBRAC expression RSQRBRAC
    """
    operands = []
    symbol_zero = AstSymbol("0", AstExprType(AstExprType.AST_NUMBER_SYMBOL, ()))
    expr_zero = AstExpression(AstOperator.AST_OP_SYMBOL, [symbol_zero])
    if len(p) == 5:
        indexed_src = AstExpression(
            AstOperator.AST_OP_SYMBOL,
            [AstSymbol(p[1], environment[p[1]])]
        )
        operands = [indexed_src, p[3], expr_zero]
    else:
        operands = [p[2], p[5], expr_zero]
    p[0] = AstExpression(AstOperator.AST_OP_INDEXING, operands)

def p_integer_range(p):
    """
    integer_range : LSQRBRAC integer_class COMMA integer_class RSQRBRAC
    """
    p[0] = [
        AstExpression(AstOperator.AST_OP_SYMBOL, [p[2]]),
        AstExpression(AstOperator.AST_OP_SYMBOL, [p[4]])
    ]

def p_integer_class(p):
    """
    integer_class : ID
                  | INTEGER
    """
    p[0] = AstSymbol(str(p[1]), AstExprType(AstExprType.AST_NUMBER_SYMBOL, ()))

def p_atom(p):
    """
    atom : core
         | array_type
    """
    p[0] = AstExpression(AstOperator.AST_OP_SYMBOL, [p[1]])

def p_array_type(p):
    """
    array_type : vector
               | matrix
    """
    rows = len(p[1])
    cols = 1
    if rows > 0 and type(p[1][0]) == "list":
        cols = len(p[1][0])
    p[0] = AstSymbol(
        "Matrix(%s)" % str(p[1]),
        AstExprType(AstExprType.AST_MATRIX_SYMBOL, (rows, cols))
    )

def p_matrix(p):
    """
    matrix : LSQRBRAC list_vectors RSQRBRAC
    """
    p[0] = p[2]

def p_vector(p):
    """
    vector : LSQRBRAC list_cores RSQRBRAC
    """
    p[0] = p[2]

def p_list_vectors(p):
    """
    list_vectors : vector COMMA list_vectors
                 | vector
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_list_cores(p):
    """
    list_cores : core rest_list_cores
               | empty
    """
    if len(p) == 3:
        p[0] = [p[1].name] + p[2]
    else:
        p[0] = []

def p_rest_list_cores(p):
    """
    rest_list_cores : COMMA core rest_list_cores
                    | empty
    """
    if len(p) == 4:
        p[0] = [p[2].name] + p[3]
    else:
        p[0] = []

def p_core(p):
    """
    core : ID
         | DOUBLE
         | INTEGER
    """
    core_type = AstExprType(AstExprType.AST_NUMBER_SYMBOL, ())
    if type(p[1]) == str:
        core_type = environment[p[1]]
    p[0] = AstSymbol(str(p[1]), core_type)

def p_math_func(p):
    """
    math_func : SQRT
              | SIN
              | COS
              | TAN
              | COT
              | LN
              | TRANSPOSE
    """
    p[0] = p[1]

def p_loop_func(p):
    """
    loop_func : SUM
              | PRODUCT
    """
    p[0] = p[1]

def p_empty(p):
    "empty :"
    p[0] = ""

parser = pyyacc.yacc()

def parse(program_text):
    """ Parses the expression description program
    """
    return parser.parse(program_text)
