import argparse
import sympy
from javaexprcodegen import JavaExprCodeGenerator
from javahessiancodegen import JavaHessianCodeGenerator
from javajacobiancodegen import JavaJacobianCodeGenerator
from exprcodegen import Variable, VariableType
from filecodewriter import FileCodeWriter
from sympy import Symbol, MatrixSymbol, Matrix

description = """
Testing
"""

def main():
    # Parsing command-line inputs
    arg_parser = argparse.ArgumentParser(description=description)
    arg_parser.parse_args()

    input_file = open("input.txt", "r")
    output_file = FileCodeWriter("output.java")

    expr_str = ""
    var_list = []
    locals = {}

    for line in input_file:
        if "var" in line:
            components = line.split()[1:]
            if len(components) > 1 and components[1] == "vector":
                vector_size = int(components[2])
                var_list.append(Variable(
                    components[0], VariableType.VECTOR, (vector_size,)))
                locals[components[0]] = Matrix(
                    MatrixSymbol(components[0], vector_size, 1))
            else:
                var_list.append(
                    Variable(components[0], VariableType.NUMBER, ()))
                locals[components[0]] = Symbol(components[0])
        else:
            if "model" in line:
                components = line.split('=')
                expr_str = components[1]

    sympy_expr = sympy.sympify(expr_str, locals)
    hessian_generator = JavaHessianCodeGenerator(var_list, sympy_expr)
    hessian_generator.gen_code(output_file)
    jacobian_generator = JavaJacobianCodeGenerator(var_list, sympy_expr)
    jacobian_generator.gen_code(output_file)

if __name__ == "__main__":
    main()
