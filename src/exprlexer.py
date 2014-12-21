import sys
import os.path as ospath

# Specify path to load ply.lexer module
plylex_path = ospath.abspath(ospath.join(
    ospath.dirname(__file__),
    "../third-party/ply-3.4"
))
sys.path.append(plylex_path)

import ply.lex as plex

# List of token names. Always required
tokens = (
    # Reserved type keywords
    "VAR",
    "VECTOR",
    "MODEL",

    # Reserved standard math functions
    "SQRT",
    "SIN",
    "COS",
    "TAN",
    "COT",

    # Math operator
    "PLUS",
    "MINUS",
    "MUL",
    "DIV",
    "EXP",
    "DOT",
    "EQUAL",

    # Bracket, parenthesis
    "LPAREN",
    "RPAREN",
    "LSQRBRAC",
    "RSQRBRAC",

    # Variable ID and Number
    "ID",
    "NUMBER"
)

reserved = {
    "sqrt" : "SQRT",
    "sin" : "SIN",
    "cos" : "COS",
    "tan" : "TAN",
    "cot" : "COT",
    "var" : "VAR",
    "vector" : "VECTOR",
    "model" : "MODEL"
}

# Rules for operators
t_PLUS = "\\+"
t_MINUS = "-"
t_MUL = "\\*"
t_DIV = "/"
t_EXP = "\\^"
t_DOT = "\\."
t_EQUAL = "="

# Rules for bracket and parenthesis
t_LPAREN = "\\("
t_RPAREN = "\\)"
t_LSQRBRAC = "\\["
t_RSQRBRAC = "\\]"

def t_NUMBER(t):
    "\d+(\.)?\d*(e(\+|-)\d+)?"
    t.value = float(t.value)
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
    "/\*(.|\\n)*?\*/"
    t.lexer.lineno += t.value.count("\n")

lexer = plex.lex()

def main():
    text = open('firstExpr.txt', 'r').read()
    lexer.input(text)
    while True:
        token = lexer.token()
        if not token:
            break
        print token.type, token.value, token.lineno

if __name__ == "__main__":
    main()
