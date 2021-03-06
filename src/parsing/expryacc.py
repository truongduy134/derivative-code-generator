import ply.yacc as pyyacc
from .exprlex import tokens
from .astdef import (
    AstConstant,
    AstExpression,
    AstExprType,
    AstOperator,
    AstSymbol,
    AstSymbolFlag
)

precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "MUL", "DIV", "DOT"),
    ("left", "EXP", "CROSS"),
    ("left", "APOSTROPHE"),
    ("right", "UMINUS")
)

environment = {}        # Map a string which is a name of an atom to its type
for_loop_vars = []


def p_file_description(p):
    """
    file_description : list_const_declarations list_var_declarations list_expr_declarations
    """
    p[2] += for_loop_vars
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
    var_declaration : basic_var_declaration
                    | basic_var_declaration COLON NODIFF
                    | basic_var_declaration COLON EQUIVALENT
    """
    p[0] = p[1]
    if len(p) == 4:
        if p[3] == "nodiff":
            # The variable is not used in differentiation
            p[0].flag = AstSymbolFlag.NO_DIFF
        else:
            p[0].flag = AstSymbolFlag.EQUIVALENT


def p_basic_var_declaration(p):
    """
    basic_var_declaration : NUMBER ID
                          | VECTOR ID LPAREN integer_and_id RPAREN
                          | MATRIX ID LPAREN integer_and_id COMMA integer_and_id RPAREN
    """
    if len(p) == 3:
        p[0] = AstSymbol(p[2], AstExprType(AstExprType.NUMBER, ()))
    elif len(p) == 6:
        p[0] = AstSymbol(p[2], AstExprType(AstExprType.VECTOR, (p[4], 1)))
    else:
        p[0] = AstSymbol(p[2], AstExprType(AstExprType.MATRIX, (p[4], p[6])))
    environment[p[0].name] = p[0].type_info


def p_list_expr_declarations(p):
    """
    list_expr_declarations : expr_declaration list_expr_declarations
                           | empty
    """
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_expr_declaration(p):
    """
    expr_declaration : EXPR ID EQUAL expression
                     | EXPR MAIN EQUAL expression
    """
    p[0] = (p[2], p[4])
    environment[p[2]] = p[4].expr_type


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
               | matrix_of_exprs
               | vector_of_exprs
    """
    num_components = len(p)
    if num_components == 2:
        p[0] = p[1]
    elif num_components == 3:
        if p[1] == "-":
            # expression : -expression
            p[0] = AstExpression(AstOperator.UMINUS, [p[2]])
        else:
            # expression : expression' (matrix transpose)
            p[0] = AstExpression(AstOperator.TRANSPOSE_SHORT, [p[1]])
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
    op_type = AstOperator.LOOP_SUM
    if p[2] == "product":
        op_type = AstOperator.LOOP_PRODUCT
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
        AstExprType(AstExprType.NUMBER, ()),
        AstSymbolFlag.USED_IN_LOOP
    )
    p[0] = AstExpression(
        AstOperator.RANGE,
        [AstExpression(AstOperator.SYMBOL, [loop_symbol])] + p[4]
    )
    for_loop_vars.append(loop_symbol)
    environment[loop_symbol.name] = loop_symbol.type_info


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
    p[0] = AstExpression(AstOperator.INDEXING, operands)


def p_vector_index(p):
    """
    vector_index : ID LSQRBRAC expression RSQRBRAC
                 | LPAREN expression RPAREN LSQRBRAC expression RSQRBRAC
    """
    operands = []
    symbol_zero = AstSymbol("0", AstExprType(AstExprType.NUMBER, ()))
    expr_zero = AstExpression(AstOperator.SYMBOL, [symbol_zero])
    if len(p) == 5:
        indexed_src = AstExpression(
            AstOperator.SYMBOL,
            [AstSymbol(p[1], environment[p[1]])]
        )
        operands = [indexed_src, p[3], expr_zero]
    else:
        operands = [p[2], p[5], expr_zero]
    p[0] = AstExpression(AstOperator.INDEXING, operands)


def p_matrix_of_exprs(p):
    """
    matrix_of_exprs : LSQRBRAC list_vector_of_exprs RSQRBRAC
    """
    p[0] = AstExpression(AstOperator.EXPR_COLLECTION, p[2])


def p_list_vector_of_exprs(p):
    """
    list_vector_of_exprs : vector_of_exprs COMMA list_vector_of_exprs
                         | vector_of_exprs
    """
    if len(p) == 2:
        p[0] = [p[1].operands]
    else:
        p[0] = [p[1].operands] + p[3]


def p_vector_of_exprs(p):
    """
    vector_of_exprs : LSQRBRAC list_expressions RSQRBRAC
    """
    p[0] = AstExpression(AstOperator.EXPR_COLLECTION, p[2])


def p_list_expressions(p):
    """
    list_expressions : expression COMMA list_expressions
                     | expression
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]


def p_integer_range(p):
    """
    integer_range : LSQRBRAC expression COMMA expression RSQRBRAC
    """
    p[0] = [p[2], p[4]]


def p_integer_class(p):
    """
    integer_class : ID
                  | INTEGER
    """
    p[0] = AstSymbol(str(p[1]), AstExprType(AstExprType.NUMBER, ()))


def p_atom(p):
    """
    atom : ID
         | DOUBLE
         | INTEGER
    """
    symbol_type = AstExprType(AstExprType.NUMBER, ())
    if type(p[1]) == str:
        symbol_type = environment[p[1]]
    ast_symbol = AstSymbol(str(p[1]), symbol_type)
    p[0] = AstExpression(AstOperator.SYMBOL, [ast_symbol])


def p_integer_and_id(p):
    """
    integer_and_id : ID
                   | INTEGER
    """
    p[0] = p[1]


def p_math_func(p):
    """
    math_func : ABS
              | SQRT
              | SIN
              | COS
              | TAN
              | COT
              | LN
              | NORM
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
