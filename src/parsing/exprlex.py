import ply.lex as pylex

# List of token names. Always required
tokens = (
    # Reserved type keywords
    "NUMBER",
    "INT"
    "VECTOR",
    "MATRIX",
    "CONST",
    "EXPR",

    "NODIFF",

    "MAIN",

    # Reserved loop keywords
    "FOR",
    "IN",
    "SUM",
    "PRODUCT",

    # Reserved standard math functions
    "SQRT",
    "SIN",
    "COS",
    "TAN",
    "COT",
    "LN",

    # Vector and matrix math functions
    "TRANSPOSE",

    # Math operator
    "PLUS",
    "MINUS",
    "MUL",
    "DIV",
    "EXP",
    "DOT",
    "CROSS",
    "EQUAL",

    # Bracket, parenthesis, punctuation
    "LPAREN",
    "RPAREN",
    "LSQRBRAC",
    "RSQRBRAC",
    "COMMA",
    "APOSTROPHE",
    "COLON",

    # Variable ID and Number
    "ID",
    "DOUBLE",
    "INTEGER"
)

reserved = {
    # Reserved standard math functions
    "sqrt" : "SQRT",
    "sin" : "SIN",
    "cos" : "COS",
    "tan" : "TAN",
    "cot" : "COT",
    "ln" : "LN",

    # Vector and matrix functions
    "transpose" : "TRANSPOSE",

    # Reserved type keywords
    "number" : "NUMBER",
    "int" : "INT"
    "vector" : "VECTOR",
    "matrix" : "MATRIX",
    "const" : "CONST",
    "expr" : "EXPR",

    # Reserved loop keywords,
    "sum" : "SUM",
    "product" : "PRODUCT",
    "for" : "FOR",
    "in" : "IN",

    "nodiff" : "NODIFF",

    "main" : "MAIN"
}

# Rules for operators
t_PLUS = "\\+"
t_MINUS = "-"
t_MUL = "\\*"
t_DIV = "/"
t_EXP = "\\^"
t_DOT = "\\."
t_CROSS = "\\#"
t_EQUAL = "="

# Rules for bracket, parenthesis and punctuation
t_LPAREN = "\\("
t_RPAREN = "\\)"
t_LSQRBRAC = "\\["
t_RSQRBRAC = "\\]"
t_COMMA = ","
t_APOSTROPHE = "'"
t_COLON = "\:"

# Double token should have higher priority to be matched than that of
# Integer token
def t_DOUBLE(t):
    "\\d+((\\.\\d*) | ((\\.\\d*)?(e[\\+-]\\d+)))"
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    "\\d+"
    t.value = int(t.value)
    return t

def t_ID(t):
    "[A-Za-z_][A-Za-z_0-9]*"
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

def t_error(t):
    """ Error handling rule
    """
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

# Token rule for line comments, block comments and whitespaces
# Simply discards the tokens
t_ignore_LINE_COMMENT = "//.*"
def t_ignore_WHITESPACES(t):
    "\\s+"
    t.lexer.lineno += t.value.count('\n')

def t_ignore_BLOCK_COMMENT(t):
    "/\\*(.|\\n)*?\\*/"
    t.lexer.lineno += t.value.count("\n")

lexer = pylex.lex()
