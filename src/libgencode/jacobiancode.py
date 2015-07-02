from abc import ABCMeta, abstractmethod

import common.util as commonutil
import libgencode.codegenutil as codegenutil
from common.vardef import VariableType
from .derivativecode import JavaDerivativeCodeGenerator

class JacobianCodeGenerator(object):
    """
    This is an abstract class for generating code to compute Jacobian vector
    for an input mathematical multivariate expression

    Public object member attributes:
        var_list : A list of Variable objects
        expr : A sympy symbolic expression
        func_name : A string representing name of the generated Jacobian method
        diff_var_list : A list of Variable objects used in differentiation
        modifier_list : A list of strings indicating modifiers for the
                        jacobian method / function, and for derivative functions
                        (such as static, private, public, etc.)

    Protected object member attributes:
        _diff_code_generator : The code generator for partial derivatives
    """

    __metaclass__ = ABCMeta

    DEFAULT_FUNC_NAME = "jacobian"
    DEFAULT_DERIVATIVE_NAME = "partialDerivative"

    def __init__(
            self,
            var_list,
            sympy_expr,
            func_name=None,
            diff_var_list=None,
            modifier_list=None):
        """ Class constructor
        """
        self.var_list = var_list
        self.expr = sympy_expr
        if func_name is None:
            self.func_name = JacobianCodeGenerator.DEFAULT_FUNC_NAME
        else:
            self.func_name = func_name
        if diff_var_list is None:
            self.diff_var_list = self.var_list
        else:
            self.diff_var_list = diff_var_list
        if modifier_list is None:
            self.modifier_list = []
        else:
            self.modifier_list = modifier_list
        self._diff_code_generator = self._get_derivative_code_generator()

    @abstractmethod
    def _get_derivative_code_generator(self):
        """ Returns the derivative code generator
        Subclass should implement this method to get a derivative code generator
        in a specific programming language
        """
        pass

    @abstractmethod
    def _gen_jacobian_code(self, file_handler):
        """ Generates code for function to compute Jacobian vector
        Subclass should implement this method to generate function code in a
        specific programming language
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        pass

    def gen_code(self, file_handler):
        """ Generates code for a function to evaluate hessian matrix
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        self._diff_code_generator.gen_code_all_first_order(file_handler)
        self._gen_jacobian_code(file_handler)

class JavaJacobianCodeGenerator(JacobianCodeGenerator):
    """
    This is a class inherited from JacobianCodeGenerator that generates Java
    code to compute Hessian matrix for an input mathematical multivariate
    expression
    """

    def __init__(
            self,
            var_list,
            sympy_expr,
            func_name=None,
            diff_var_list=None,
            modifier_list=None,
            class_name=None):
        """ Class constructor
        """
        JacobianCodeGenerator.__init__(
            self, var_list, sympy_expr, func_name,
            diff_var_list, modifier_list)
        self.class_name = class_name

    def _get_derivative_code_generator(self):
        """ Returns the derivative code generator in Java
        """
        return JavaDerivativeCodeGenerator(
            self.var_list,
            self.expr,
            JacobianCodeGenerator.DEFAULT_DERIVATIVE_NAME,
            self.diff_var_list,
            self.modifier_list)

    def __gen_jacobian_declaration(self, file_handler):
        """ Generates Java code for Jacobian function declaration
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        func_declaration = codegenutil.get_java_func_declaration(
            self.func_name, "double[]", self.var_list, self.modifier_list)
        if self.class_name:
            func_declaration += (" throws NoSuchMethodException, "
                                 "IllegalAccessException, "
                                 "java.lang.reflect.InvocationTargetException")
        file_handler.write(func_declaration + " {\n")

    def __gen_simple_jacobian_body(self, file_handler):
        """ Generates Java code for the body of the function to compute
        Jacobian vector

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        num_diff_var = self._diff_code_generator.get_num_expanded_diff_var()
        param_list = ", ".join([var.name for var in self.var_list])
        temp_vector = "__temp"

        file_handler.write("double[] %s = new double[%d];\n" % (
            temp_vector, num_diff_var))
        for i in xrange(num_diff_var):
            file_handler.write("%s[%d] = %s(%s);\n" % (
                temp_vector, i,
                self._diff_code_generator.get_derivative_func_name(
                    i, None, True),
                param_list))
        file_handler.write("return %s;\n" % temp_vector)

    def __gen_reflect_jacobian_body(self, file_handler):
        """ Generates Java code for the body of the function to compute
        Jacobian vector with Java Reflection API

        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        num_diff_var = self._diff_code_generator.get_num_expanded_diff_var()
        num_func_args = len(self.var_list)
        temp_vector = "__temp"

        arg_class_list_var_name = "argClasses"
        main_class_var_name = (commonutil.lower_first_char(self.class_name) +
            "Class")
        method_name_var_name = "methodName"
        method_var_name = "method"

        param_list = ", ".join([var.name for var in self.var_list])

        file_handler.write("double[] %s = new double[%d];\n" % (
            temp_vector, num_diff_var))
        file_handler.write("Class %s = new %s().getClass();\n" % (
            main_class_var_name, self.class_name))
        # Argument type list
        file_handler.write("Class[] %s = new Class[%d];\n" % (
            arg_class_list_var_name, num_func_args))
        for arg_ind in xrange(num_func_args):
            func_arg = self.var_list[arg_ind]
            type_str = "double"
            if func_arg.var_type == VariableType.VECTOR:
                type_str += "[]"
            elif func_arg.var_type == VariableType.MATRIX:
                type_str += "[][]"
            file_handler.write("%s[%d] = %s.class;\n" % (
                arg_class_list_var_name, arg_ind, type_str))

        # Jacobian code
        file_handler.write("for (int i = 0; i < %d; ++i) {\n" % num_diff_var)
        file_handler.tab()
        diff_base_name = self._diff_code_generator.base_func_name
        file_handler.write("String %s = \"%s\" + Integer.toString(i);\n" % (
            method_name_var_name, diff_base_name + "_"))
        rhs_code = "%s.getDeclaredMethod(%s, %s);\n" % (
            main_class_var_name, method_name_var_name, arg_class_list_var_name)
        file_handler.write("java.lang.reflect.Method %s = %s" % (
            method_var_name, rhs_code))
        invoked_obj = "this"
        if "static" in self.modifier_list:
            invoked_obj = "null"
        file_handler.write("%s[i] = (Double) %s.invoke(%s, %s);\n" % (
            temp_vector, method_var_name, invoked_obj, param_list))
        file_handler.untab()
        file_handler.write("}\n")
        file_handler.write("return %s;\n" % temp_vector)

    def _gen_jacobian_code(self, file_handler):
        """ Generates Java code for function to compute Jacobian vector
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        self.__gen_jacobian_declaration(file_handler)
        # Function body
        file_handler.tab()
        if self.class_name:
            self.__gen_reflect_jacobian_body(file_handler)
        else:
            self.__gen_simple_jacobian_body(file_handler)
        file_handler.untab()
        file_handler.write("}\n")
