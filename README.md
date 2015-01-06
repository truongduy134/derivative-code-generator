derivative-code-generator
=========================

The script can be used to generate code (currently Java supported) to calculate partial derivatives, and Jacobian vector and Hessian matrix of an input mathematics expression.

TO-DO Lists
=========================
- Support declaring matrices / vectors with variable sizes
- ~~Support looping and summation (or product) of many operands~~
- ~~Allow constant declaration in expression description language~~
- ~~Convert 1 x 1 matrix result to a number~~
- ~~Construct AST as a result of applying expryacc (Refactor whole expryacc.py and exprparser.py)~~
- Restructure AST types in astdef.py
- Unify vectors and matrices
- Better error handling and error messages in parsing phase
- Support more functions / operations such as abs, vector norm, etc.
- Add unit tests and necessary scripts
- Generate code for C++, and other languages!
- Refactor code (especially get_operator_type)
