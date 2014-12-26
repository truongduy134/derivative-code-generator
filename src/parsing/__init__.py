__all__ = ['exprparser']

# Specify path to load ply.yacc module
import sys
import os.path as ospath

ply_path = ospath.abspath(ospath.join(
    ospath.dirname(__file__),
    "../../third-party/ply-3.4"
))
sys.path.append(ply_path)
