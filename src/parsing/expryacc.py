import ply.yacc as pyyacc
from .exprlex import tokens

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MUL', 'DIV', 'DOT', 'CROSS'),
    ('left', 'EXP'),
    ('right', 'UMINUS')
)

def p_file_description(p):
    "file_description : list_var_declarations expr_declaration"
    p[0] = p[1] + "\n" + p[2]

def p_list_var_declarations(p):
    """
    list_var_declarations : var_declaration list_var_declarations
                          | empty
    """
    if len(p) == 3:
        p[0] = p[1] + "\n" + p[2]
    else:
        p[0] = ""

def p_var_declaration(p):
    """
    var_declaration : VAR ID
                    | VAR ID VECTOR INTEGER
    """
    if len(p) == 3:
        p[0] = p[1] + " " + p[2]
    else:
        p[0] = p[1] + " " + p[2] + " " + p[3] + " " + str(p[4])

def p_expr_declaration(p):
    "expr_declaration : MODEL EQUAL expression"
    p[0] = p[1] + "=" + p[3]

def p_expression(p):
    """
    expression : expression PLUS expression
               | expression MINUS expression
               | expression MUL expression
               | expression DIV expression
               | expression DOT expression
               | expression EXP expression
               | expression CROSS expression
               | LPAREN expression RPAREN
               | MINUS expression %prec UMINUS
               | math_func_call
               | vector_index
               | matrix_index
               | atom
    """
    num_components = len(p)
    if num_components == 2:
        # expression : atom
        p[0] = p[1]
    elif num_components == 3:
        # expression : -expression
        p[0] = "-" + p[2]
    elif p[1] == "(":
        # expression : (expression)
        p[0] = "(%s)" % p[2]
    elif p[2] == "^":
        # In the expression specfication language, ^ denotes exponentiation
        # However, sympy uses ** for exponentiation
        p[0] = p[1] + "**" + p[3]
    elif p[2] == ".":
        # Dot product
        p[0] = "%s.dot(%s)" % (p[1], p[3])
    elif p[2] == "#":
        # Cross product
        p[0] = "%s.cross(%s)" % (p[1], p[3])
    else:
        # Expression with normal +, -, *, / operators
        p[0] = p[1] + p[2] + p[3]

def p_math_func_call(p):
    """
    math_func_call : math_func LPAREN expression RPAREN
    """
    p[0] = "%s(%s)" % (p[1], p[3])

def p_matrix_index(p):
    """
    matrix_index : vector_index LSQRBRAC expression RSQRBRAC
    """
    p[0] = p[1] + "[" + p[3] + "]"

def p_vector_index(p):
    """
    vector_index : ID LSQRBRAC expression RSQRBRAC
                 | LPAREN expression RPAREN LSQRBRAC expression RSQRBRAC
    """
    if len(p) == 5:
        p[0] = p[1] + "[" + p[3] + "]"
    else:
        p[0] = "(" + p[2] + ")[" + p[5] + "]"

def p_atom(p):
    """
    atom : core
         | vector
    """
    p[0] = p[1]

def p_vector(p):
    """
    vector : LSQRBRAC list_cores RSQRBRAC
    """
    p[0] = "Matrix([%s])" % p[2]

def p_list_cores(p):
    """
    list_cores : core rest_list_cores
               | empty
    """
    if len(p) == 3:
        p[0] = p[1] + p[2]
    else:
        p[0] = ""

def p_rest_list_cores(p):
    """
    rest_list_cores : COMMA core rest_list_cores
                    | empty
    """
    if len(p) == 4:
        p[0] = "," + p[2] + p[3]
    else:
        p[0] = ""

def p_core(p):
    """
    core : ID
         | DOUBLE
         | INTEGER
    """
    p[0] = str(p[1])

def p_math_func(p):
    """
    math_func : SQRT
              | SIN
              | COS
              | TAN
              | COT
    """
    p[0] = p [1]

def p_empty(p):
    "empty :"
    pass

parser = pyyacc.yacc()

def parse(program_text):
    """ Parses the expression description program
    """
    return parser.parse(program_text)

"""
def main():
    text = open("firstExpr.txt", "r").read()
    result = parser.parse(text)
    print result

if __name__ == "__main__":
    main()
"""
