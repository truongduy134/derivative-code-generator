from exprcodegen import OperatorType, ExprCodeGenerator

class JavaExprCodeGenerator(ExprCodeGenerator):
    """
    This is a class inherited from ExprCodeGenerator that generates Java code
    to compute the input math expressions
    """

    def __init__(
            self,
            var_list,
            sympy_expr,
            func_name=None,
            tab_type=None,
            tab_size=None,
            temp_prefix=None):
        """ Constructor
        """
        ExprCodeGenerator.__init__(
            self, var_list, sympy_expr, func_name, tab_type, tab_size,
            temp_prefix)
    
    def _gen_func_declaration(
            self,
            file_handler):
        """ Generates Java code for function declaration
        Args:
            file_handler : an output file handler to write the code to
        """
        header = "double " + self.func_name + "("
        is_first = True
        for var in self.var_list:
            if is_first:
                is_first = False
            else:
                header += ", "
            header += "double " + var.name 
        header += ") {\n"
        file_handler.write(header)

    def _gen_return_code(
            self,
            result_holder_name,
            file_handler):
        """ Generates Java code at the end of function (for returning 
        results, etc.)
        Args:
            result_holder_name : a string for a variable name that holds the
                final result of the whole expression
            file_handler : an output file handler to write the code to
        """
        return_stm = self._get_indent_string()
        return_stm += "return " + result_holder_name + ";\n"
        file_handler.write(return_stm)
        file_handler.write("}\n\n")

    def _gen_code_operator(
            self,
            op_type,
            operand_names,
            result_holder_name,
            file_handler):
        """ Generates Java code for operators
        Args:
            op_type : a variable of type OperatorType indicating operator type
            operand_names : a list of strings of operand names
            result_holder_name : a string for a variable name that holds the
                final result
            file_handler : an output file handler to write the code to
        Example:
            self._gen_code_operator(OperatorType.ADD_REAL, ['a', 'b', 'c'],
                'result', outfile) generates code for the statement
                result = a + b + c 
        """
        statement_str = self._get_indent_string()
        statement_str += "double " + result_holder_name + " = "
        if op_type == OperatorType.POW_REAL:
            statement_str += ("Math.pow(" + operand_names[0] + ", " +
                              operand_names[1] + ")")
        elif op_type in [OperatorType.ADD_REAL, OperatorType.MUL_REAL]:
            op_char = '+' if op_type == OperatorType.ADD_REAL else '*'
            statement_str += op_char.join(operand_names)
        else:
            # Better handling of this case (Throw exception?)
            statement_str += operand_names[0]
        statement_str += ";\n"
        file_handler.write(statement_str)
