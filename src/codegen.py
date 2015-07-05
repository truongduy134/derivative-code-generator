#!/usr/bin/env python

import argparse
import json
import os
import os.path as ospath

from collections import defaultdict

import parsing.exprparser as exprparser
from common import sympyutils
from libgencode.codegenutil import FileCodeWriter
from libgencode.exprclasscode import JavaExprClassCodeGenerator

DESCRIPTION = """
The program reads a file specifying a multivariate arithmetic expression, and
generates code to compute its value, its jacobian vector, and its hessian
matrix. The program supports various programming languages for the generated
code.
"""

SUPPORTED_LANGS = ["java"]
DEFAULT_LANG = "java"


def init_argument_parser():
    """ Creates an argument parser and adds specifications for command-line
    arguments for the expression code generation program.

    Returns:
        arg_parser : An initialized ArgumentParser object with properties
                     lang, dest, cname, exprfile
    """
    arg_parser = argparse.ArgumentParser(description=DESCRIPTION)
    # Optional arguments
    arg_parser.add_argument(
        "--config", "-c",
        type=str,
        default="",
        help="The file path to the json file containing configuration for "
             "code generation, such as package name, class name, language, etc."
             " Note that the configuration parameters specified in the command "
             "line have higher priority than those in the configuration file "
             "(which means they can override what are specified in the "
             "configuration file)."
    )
    arg_parser.add_argument(
        "--cname", "-n",
        type=str,
        default="",
        help="The name of the class that encapsulates generated code. "
             "By default, the name if the expression specification file will "
             "be used for the class name, with the first character is made "
             "to be uppercase"
    )
    arg_parser.add_argument(
        "--dest", "-d",
        type=str,
        default="",
        help="Destination directory that holds the generated code files. "
             "By default, the current directory is used."
    )
    arg_parser.add_argument(
        "--lang", "-l",
        type=str,
        default="",
        help="Programming language that the generated code is in. "
             "The default language is Java."
    )
    arg_parser.add_argument(
        "--nohessian",
        action="store_true",
        default=False,
        help="Flag to turn off code generation for Hessian matrix"
    )

    # Positional arguments
    arg_parser.add_argument(
        "exprfile", type=str,
        help="The expression specification file name or path."
    )

    return arg_parser


def get_code_gen_config(args):
    """ Gets a dictionary containing configuration information for code
    generation
    Args:
        args : Object returned by ArgumentParser containing command-line
               arguments passed to the script

    Returns:
        code_gen_config : A dictionary with key-value pairs indicating
                          configuration for code generation such as class name,
                          package name, destination directory, and flag whether
                          to generate Hessian code or not
    Raises:
        IOError : An error if the configuration file path is specified, but
                  the file content is not a JSON object
        NotImplementedError: An error if the specified language is not yet
                             supported by the program
    """
    config_file_path = args.config
    code_gen_config = defaultdict(str)
    if config_file_path:
        with open(config_file_path, "r") as config_file:
            config = json.load(config_file)
            if not isinstance(config, dict):
                raise IOError(
                    "The file at path %s is not a JSON object file" %
                    config_file_path
                )
            for key, value in config.iteritems():
                code_gen_config[key.lower()] = value

    # Language
    lang = args.lang if args.lang else code_gen_config["lang"]
    if not lang:
        lang = DEFAULT_LANG
    lang = lang.lower()
    if lang not in SUPPORTED_LANGS:
        raise NotImplementedError(
            "The specified language: %s is not supported" % lang)
    code_gen_config["lang"] = lang

    # Class name
    classname = args.cname if args.cname else code_gen_config["classname"]
    if not classname:
        filename = ospath.basename(args.exprfile)
        filename = ospath.splitext(filename)[0]     # Remove extension
        classname = filename[0].upper() + filename[1:]
    code_gen_config["classname"] = classname

    # Destination directory
    dest = args.dest if args.dest else code_gen_config["dest"]
    if not dest:
        dest = os.getcwd()
    code_gen_config["dest"] = dest

    # Hessian Flag
    code_gen_config["nohessian"] = args.nohessian

    return dict(code_gen_config)


def get_code_generator(lang, var_list, diff_var_list, sympy_expr, config):
    """ Gets the corresponding code generator for the input programming language
    Args:
        lang : a string that represents a programming language
        var_list : A list of Variable objects
        diff_var_list : A list of Variable objects that are used as
                        differentation variables
        sympy_expr : A sympy symbolic expression
        config : A dictionary with key-value pairs indicating configuration for
                 code generation such as class name, package name, etc.

    Returns:
        code_generator : an instance of exprclasscode.ExprClassCodeGenerator
    Raises:
        NotImplementedError : An error if the specified language is not yet
                              supported by the program
    """
    normalized_lang = lang.lower()
    if normalized_lang == "java":
        return JavaExprClassCodeGenerator(
            var_list, sympy_expr, config, diff_var_list)
    else:
        raise NotImplementedError(
            "The specified language: %s is not supported" % lang)


def gen_code(var_list, diff_var_list, sympy_expr, code_gen_config):
    """ Generates expression class code
    Args:
        var_list : A list of Variable objects
        diff_var_list : A list of Variable objects that are used as
                        differentation variables
        sympy_expr : A sympy symbolic expression
        code_gen_config : A dictionary with key-value pairs indicating
                          configuration for code generation such as class name,
                          package name, destination directory, language, etc.
    """
    code_generator = get_code_generator(
        code_gen_config["lang"],
        var_list,
        diff_var_list,
        sympy_expr,
        code_gen_config)
    output_file_path = ospath.join(
        code_gen_config["dest"], code_generator.default_file_name())
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

    code_gen_config = get_code_gen_config(args)

    with open(args.exprfile, "r") as input_file:
        var_list, diff_var_list, sympy_expr = (
            exprparser.parse_expr_specification(input_file.read())
        )
        sympyutils.distinguish_dummy_vars(sympy_expr)
        gen_code(var_list, diff_var_list, sympy_expr, code_gen_config)

if __name__ == "__main__":
    main()
