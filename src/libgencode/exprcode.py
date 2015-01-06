from abc import ABCMeta, abstractmethod

import libgencode.codegenutil as codegenutil
from codegenutil import OperatorType
from common.vardef import VariableType

class ExprCodeGenerator(object):
    """
    This is an abstract class for generating code for an input
    mathematical expression

    Public object member attributes:
        var_list : A list of Variable objects
        expr : A sympy symbolic expression
        func_name : A string representing function name
        modifier_list : A list of strings indicating modifiers for the
                    method / function (such as static, private, public, etc.)
        temp_var_prefix : A string indicating the name that is used as a prefix
                   for temporary variables in code generation

    Protected object member attributes:
        _var_dict : A dictionary that maps variable name to the Variable
                    structure itself

    Private object member attributes:
        __num_temp_var_used : An integer indicating the number of temporary
                              variables used so far in code generation
    """

    __metaclass__ = ABCMeta

    DEFAULT_TEMP_NAME = "__temp"
    DEFAULT_FUNC_NAME = "evaluate"

    def __init__(
            self,
            var_list,
            sympy_expr,
            func_name=None,
            modifier_list=None,
            temp_prefix=None):
        """ Class constructor
        """
        self.var_list = var_list
        self.expr = sympy_expr
        if func_name is None:
            self.func_name = ExprCodeGenerator.DEFAULT_FUNC_NAME
        else:
            self.func_name = func_name
        if temp_prefix is None:
            self.temp_var_prefix = ExprCodeGenerator.DEFAULT_TEMP_NAME
        else:
            self.temp_var_prefix = temp_prefix
        if modifier_list is None:
            self.modifier_list = []
        else:
            self.modifier_list = modifier_list
        self.__num_temp_var_used = 0
        self._var_dict = {var_obj.name: var_obj for var_obj in self.var_list}

    def _get_nxt_temp_var_name(self):
        """ Gets the name that can be used for the next temporary variable.
        Returns:
            A string that can be used as the name for the next temporary
            variable declared during the code generation
        """
        next_name = self.temp_var_prefix + "_" + str(self.__num_temp_var_used)
        self.__num_temp_var_used += 1
        return next_name

    @abstractmethod
    def _gen_func_declaration(self, file_handler):
        """ Generates code for function declaration
        Subclass should implement this method to generate function
        declaration (prototype) in a specific programming language
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        pass

    @abstractmethod
    def _gen_return_code(self, result_holder_name, file_handler):
        """ Generates code at the end of function (for returning results, etc.)
        Subclass should implement this method to generate code in a specific
        programming language
        Args:
            result_holder_name : a string for a variable name that holds the
                final result of the whole expression
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        pass

    @abstractmethod
    def _gen_code_expr(self, sympy_expr, file_handler):
        """ Generates code for a function to evaluate input expression
        if necessary. If the expression is a singleton, no code is generated
        Subclass should implement this method to generate code in a specific
        programming language

        Args:
            sympy_expr : a sympy expression that needs code generation
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        Returns:
            A string representing the name of the variable holding the final
            result when evaluting the expression
        Example:
            1) d = self._gen_code_expr(a + b * c, file_handler) generates code
            to compute the expression a + b * c; and d is the variable name such
            that d = a + b * c
            2) d = self._gen_code_expr(a, file_handler) does not generate
            any code. It simply returns a string 'a' representing the variable
            holding the final value
            3) d = self._gen_code_expr(m[0][5], file_handler) does not
            generate any code. It simply return a string 'm[0][5]'
            representing the variable holding final value
        """
        pass

    def gen_code(self, file_handler):
        """ Generates code for a function to evaluate the input expression
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        self._gen_func_declaration(file_handler)
        file_handler.tab()
        final_var_name = self._gen_code_expr(self.expr, file_handler)
        file_handler.untab()
        self._gen_return_code(final_var_name, file_handler)

class JavaExprCodeGenerator(ExprCodeGenerator):
    """
    This is a class inherited from ExprCodeGenerator that generates Java code
    to compute the input math expressions
    """

    SUPPORT_TRIGO_FUNCS = {
        OperatorType.SIN_REAL: "Math.sin",
        OperatorType.COS_REAL: "Math.cos",
        OperatorType.TAN_REAL: "Math.tan",
    }

    def __init__(
            self,
            var_list,
            sympy_expr,
            func_name=None,
            modifier_list=None,
            temp_prefix=None):
        """ Constructor
        """
        ExprCodeGenerator.__init__(
            self, var_list, sympy_expr, func_name, modifier_list, temp_prefix)

    def _gen_func_declaration(
            self,
            file_handler):
        """ Generates Java code for function declaration
        Args:
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        func_declaration = codegenutil.get_java_func_declaration(
            self.func_name, "double", self.var_list, self.modifier_list)
        file_handler.write(func_declaration + " {\n")

    def _gen_return_code(
            self,
            result_holder_name,
            file_handler):
        """ Generates Java code at the end of function (for returning
        results, etc.)
        Args:
            result_holder_name : a string for a variable name that holds the
                final result of the whole expression
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        """
        return_stm = "return %s;\n" % result_holder_name
        file_handler.tab()
        file_handler.write(return_stm)
        file_handler.untab()
        file_handler.write("}\n\n")

    def __gen_arr_access_code(
            self,
            var_obj,
            index_tuple):
        """ Generates Java code for array / matrix element access
        Args:
            var_obj : an object containing information about the
                      array / matrix variable, such as name, type, dimension
            index_tuple : a tuple indicating the index of the element accessed
        Returns:
            A string representing the code to access array / matrix element
        """
        code = var_obj.name
        if var_obj.var_type == VariableType.VECTOR:
            real_ind = 0
            for index in index_tuple:
                if index > 0:
                    real_ind = index
            code += "[%d]" % real_ind
        else:
            for index in index_tuple:
                code += "[%d]" % index
        return code

    def __gen_code_loop(self, sympy_expr, file_handler):
        """ Generates Java code for a function to evaluate loop operation (e.g.
        taking sum or product over a sequence of elements)

        Args:
            sympy_expr : a sympy expression that needs code generation
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        Returns:
            A string representing the name of the variable holding the final
            result when evaluating the expression
        """
        operands = sympy_expr.args
        expr_op_type = codegenutil.get_operator_type(sympy_expr)
        temp_var_name = self._get_nxt_temp_var_name()

        init_value = 0.0
        if expr_op_type == OperatorType.PRODUCT_LOOP:
            init_value = 1.0
        file_handler.write("double %s = %f;\n" % (temp_var_name, init_value))
        for loop_range in operands[1:]:
            var_loop = str(loop_range[0])
            start_val = str(loop_range[1])
            if codegenutil.get_operator_type(loop_range[1]) == OperatorType.NUMBER:
                start_val = str(int(loop_range[1].evalf()))
            end_val = str(loop_range[2])
            if codegenutil.get_operator_type(loop_range[2]) == OperatorType.NUMBER:
                end_val = str(int(loop_range[2].evalf()))
            step = "1"
            loop_statement = "for (int %s = %s; %s <= %s; %s += %s) {\n" % (
                var_loop, start_val, var_loop, end_val, var_loop, step)
            file_handler.write(loop_statement)
            file_handler.tab()

        inner_temp_var_name = self._gen_code_expr(operands[0], file_handler)
        op_str = "+="
        if expr_op_type == OperatorType.PRODUCT_LOOP:
            op_str = "*="
        file_handler.write("%s %s %s;\n" % (
            temp_var_name, op_str, inner_temp_var_name))

        for i in xrange(len(operands[1:])):
            file_handler.untab()
            file_handler.write("}\n")

        return temp_var_name

    def _gen_code_expr(self, sympy_expr, file_handler):
        """ Generates Java code for a function to evaluate input expression
        if necessary. If the expression is a singleton, no code is generated

        Args:
            sympy_expr : a sympy expression that needs code generation
            file_handler : an instance of FileCodeWriter that handles writing
                           generated code to a file.
        Returns:
            A string representing the name of the variable holding the final
            result when evaluating the expression
        """
        expr_op_type = codegenutil.get_operator_type(sympy_expr)

        if OperatorType.is_singleton_op(expr_op_type):
            if expr_op_type == OperatorType.NUMBER:
                final_var_str = str(sympy_expr.evalf())
            elif expr_op_type == OperatorType.SYMBOL:
                final_var_str = str(sympy_expr)
            else:
                # Matrix / Vector access
                var_name = sympy_expr.args[0].name
                index_tuple = sympy_expr.args[1:]
                final_var_str = self.__gen_arr_access_code(
                    self._var_dict[var_name], index_tuple)
            return final_var_str

        if expr_op_type in [OperatorType.SUM_LOOP, OperatorType.PRODUCT_LOOP]:
            # Handle loop operation seperately
            return self.__gen_code_loop(sympy_expr, file_handler)

        # Sympy expression is not a singleton nor loop operation
        final_var_str = self._get_nxt_temp_var_name()
        operands = sympy_expr.args
        operand_names = [self._gen_code_expr(operand, file_handler)
                         for operand in operands]

        statement_str = "double %s = " % final_var_str
        if expr_op_type == OperatorType.POW_REAL:
            statement_str += "Math.pow(%s, %s)" % (
                operand_names[0], operand_names[1])
        elif expr_op_type == OperatorType.LOG_REAL:
            statement_str += "Math.log(%s)" % operand_names[0]
        elif expr_op_type in JavaExprCodeGenerator.SUPPORT_TRIGO_FUNCS:
            statement_str += "%s(%s)" % (
                JavaExprCodeGenerator.SUPPORT_TRIGO_FUNCS[expr_op_type],
                operand_names[0])
        elif expr_op_type == OperatorType.COT_REAL:
            statement_str += "Math.sin(%s) / Math.cos(%s)" % (
                operand_names[0], operand_names[0])
        elif expr_op_type in [OperatorType.ADD_REAL, OperatorType.MUL_REAL]:
            op_char = " + " if expr_op_type == OperatorType.ADD_REAL else " * "
            statement_str += op_char.join(operand_names)
        else:
            # Operators in which we do not know how to generate code
            raise Exception(
                "Cannot generate code for operator %s" % expr_op_type)

        statement_str += ";\n"
        file_handler.write(statement_str)
        return final_var_str
