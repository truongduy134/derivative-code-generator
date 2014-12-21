import argparse
import os
import os.path as ospath
import sympy

import exprparser
from codegenutil import Variable, VariableType, FileCodeWriter
from sympy import Symbol, MatrixSymbol, Matrix
from exprclasscode import JavaExprClassCodeGenerator

DESCRIPTION = """
The program reads a file specifying a multivariate arithmetic expression, and
generates code to compute its value, its jacobian vector, and its hessian
matrix. The program supports various programming languages for the generated
code.
"""

SUPPORTED_LANGS = ["java"]

def init_argument_parser():
    """ Creates an argument parser and adds specifications for command-line
    arguments for the expression code generation program.

    Returns:
        arg_parser : An initialized ArgumentParser object with properties
                     lang, dest, cname, exprfile
    """
    arg_parser = argparse.ArgumentParser(description=DESCRIPTION)
    arg_parser.add_argument(
        "--lang", "-l",
        type=str,
        default="java",
        help="Programming language that the generated code is in. "
             "The default language is java."
    )
    arg_parser.add_argument(
        "--dest", "-d",
        type=str,
        default=os.getcwd(),
        help="Destination directory that holds the generated code files. "
             "By default, the current directory is used."
    )
    arg_parser.add_argument(
        "--cname", "-c",
        type=str,
        default="",
        help="The name of the class that encapsulates generated code. "
             "By default, the name if the expression specification file will "
             "be used for the class name, with the first character is made "
             "to be uppercase"
    )
    arg_parser.add_argument(
        "exprfile", type=str,
        help="The expression specification file name or path."
    )
    return arg_parser

def get_code_generator(lang, var_list, sympy_expr, classname):
    """ Gets the corresponding code generator for the input programming language
    Args:
        lang : a string that represents a programming language
        var_list : A list of Variable objects
        sympy_expr : A sympy symbolic expression
        classname : Name of the class that encapsulates expression code

    Returns:
        code_generator : an instance of exprclasscode.ExprClassCodeGenerator
    Raises:
        NotImplementedError : An error if the specified language is not yet
                              supported by the program
    """
    normalized_lang = lang.lower()
    if normalized_lang == "java":
        return JavaExprClassCodeGenerator(var_list, sympy_expr, classname)
    else:
        raise NotImplementedError(
            "The specified language: %s is not supported" % lang)

def gen_code(var_list, sympy_expr, args):
    """ Generates expression class code
    Args:
        var_list : A list of Variable objects
        sympy_expr : A sympy symbolic expression
        args : An object that contains all command-line arguments passed to
               the program
    """
    classname = args.cname
    if not classname:
        filename = ospath.basename(args.exprfile)
        filename = ospath.splitext(filename)[0]     # Remove extension
        classname = filename[0].upper() + filename[1:]
    code_generator = get_code_generator(
        args.lang, var_list, sympy_expr, classname)
    output_file_path = ospath.join(
        args.dest, code_generator.default_file_name())
    with FileCodeWriter(output_file_path) as output_file:
        code_generator.gen_code(output_file)

def main():
    """ Main function that reads the expression specification file, does
    lexing and grammar parsing, and generates the code for the expression class
    in the specified language.
    """
    # Parsing command-line inputs
    arg_parser = init_argument_parser()
    args = arg_parser.parse_args()

    normalized_lang = args.lang.lower()
    if normalized_lang not in SUPPORTED_LANGS:
        raise NotImplementedError(
            "The specified language: %s is not supported" % args.lang)

    with open(args.exprfile, "r") as input_file:
        # Do simple lexical and syntax analysis
        program_lines = exprparser.parse_expr_desc_file(input_file.read())

        expr_str = ""
        var_list = []
        sympy_locals = {}

        for line in program_lines.split("\n"):
            if "var" in line:
                components = line.split()[1:]
                if len(components) > 1 and components[1] == "vector":
                    vector_size = int(components[2])
                    var_list.append(Variable(
                        components[0], VariableType.VECTOR, (vector_size,)))
                    sympy_locals[components[0]] = Matrix(
                        MatrixSymbol(components[0], vector_size, 1))
                else:
                    var_list.append(
                        Variable(components[0], VariableType.NUMBER, ()))
                    sympy_locals[components[0]] = Symbol(components[0])
            else:
                if "model" in line:
                    components = line.split('=')
                    expr_str = components[1]
        sympy_expr = sympy.sympify(expr_str, sympy_locals)
        gen_code(var_list, sympy_expr, args)

if __name__ == "__main__":
    main()
