#!/usr/bin/env python

from setuptools import setup

LONG_DESCRIPTION = """
DerivativeCodeGenerator is a script that takes in an expression specification
program which contains details of a mathematical expression. The script then
generates programs with functions to evaluate the expression itself, and its
Jacobian vector and Hessian matrix in a programming language specified by user
(such as Java, C++, etc.)
"""

PACKAGE_TO_DIR = {
    "common":  "src/common",
    "libgencode": "src/libgencode",
    "parsing": "src/parsing",
    "ply": "third-party/ply-3.4/ply"
}

REQUIRED_SYMPY_VERSION = '0.7.6'

setup(
    name="DerivativeCodeGenerator",
    version="0.0.1",
    description="Derivative Code Generator Script",
    long_description=LONG_DESCRIPTION,
    license="MIT",
    author="Nguyen Truong Duy",
    author_email="truongduy134@gmail.com",
    maintainer="Nguyen Truong Duy",
    maintainer_email="truongduy134@gmail.com",
    url="https://github.com/truongduy134/derivative-code-generator",
    package_dir=PACKAGE_TO_DIR,
    packages=['common', 'libgencode', 'parsing', 'ply'],
    scripts=["src/codegen.py"],
    install_requires=["sympy>=%s" % REQUIRED_SYMPY_VERSION])
