import sys
import os.path as ospath

# Specify path to load ply.yacc module
plyyacc_path = ospath.abspath(ospath.join(
    ospath.dirname(__file__),
    "../third-party/ply-3.4"
))
sys.path.append(plyyacc_path)

import ply.yacc as pyyacc
#import exprlexer
from exprlexer import tokens

def p_var_declaration(p):
    'vardeclc : VAR ID'
    p[0] = 'declare var ' + p[2]

parser = pyyacc.yacc()

def main():
    text = open('firstExpr.txt', 'r').read()
    result = parser.parse(text)
    print result

if __name__ == "__main__":
    main()
