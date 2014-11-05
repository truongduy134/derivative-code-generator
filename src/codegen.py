import argparse
import sympy
from codegenutil import Variable, VariableType
from exprcodegen import JavaExprCodeGenerator
from hessiancodegen import JavaHessianCodeGenerator
from jacobiancodegen import JavaJacobianCodeGenerator
from filecodewriter import FileCodeWriter
from sympy import Symbol, MatrixSymbol, Matrix
from javainterfacecodegen import JavaLeastSquareInterfaceGenerator

description = """
Testing
"""

def main():
    # Parsing command-line inputs
    arg_parser = argparse.ArgumentParser(description=description)
    arg_parser.parse_args()

    input_file = open("input.txt", "r")
    output_file = FileCodeWriter("LeastSquareProblem.java")

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
    hessian_generator = JavaHessianCodeGenerator(var_list, sympy_expr, modifier_list=["public"])
    hessian_generator.gen_code(output_file)
    jacobian_generator = JavaJacobianCodeGenerator(var_list, sympy_expr, modifier_list=["public"])
    jacobian_generator.gen_code(output_file)

    interface_writer = FileCodeWriter(
        JavaLeastSquareInterfaceGenerator.DEFAULT_INTERFACE_NAME + ".java")
    java_igenerator = JavaLeastSquareInterfaceGenerator(var_list)
    java_igenerator.gen_code(interface_writer)

if __name__ == "__main__":
    main()
