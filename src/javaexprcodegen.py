from exprcodegen import OperatorType, ExprCodeGenerator, VariableType

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
        header = "double %s (" % self.func_name
        is_first = True
        for var in self.var_list:
            if is_first:
                is_first = False
            else:
                header += ", "
            dimension_size = len(var.dimension)
            type_decl = "double" + "[]" * dimension_size
            header += type_decl + " " + var.name
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
        return_stm += "return %s;\n" % result_holder_name
        file_handler.write(return_stm)
        file_handler.write("}\n\n")

    def _gen_arr_access_code(
            self,
            var_obj,
            index_tuple):
        """ Generates Java code for array / matrix element access
        Args:
            var_obj : an object containing information about the 
                      array / matrix variable, such as name, type, dimension
            index_tuple : a tuple indicating the index of the element accessed
            file_handler : an output file handler to write the code to
        Returns:
            A string representing the code to access array / matrix element
        """
        code = var_obj.name;
        if var_obj.var_type == VariableType.VECTOR:
            real_ind = 0;
            for index in index_tuple:
                if index > 0:
                    real_ind = index
            code += "[%d]" % real_ind
        else:    
            for index in index_tuple:
                code += "[%d]" % index
        return code

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
        statement_str += "double %s = " % result_holder_name
        if op_type == OperatorType.POW_REAL:
            statement_str += "Math.pow(%s, %s)" % (
                operand_names[0], operand_names[1])
        elif op_type in JavaExprCodeGenerator.SUPPORT_TRIGO_FUNCS:
            statement_str += "%s(%s)" % (
                JavaExprCodeGenerator.SUPPORT_TRIGO_FUNCS[op_type],
                operand_names[0])
        elif op_type == OperatorType.COT_REAL:
            statement_str += "Math.sin(%s) / Math.cos(%s)" % (
                operand_names[0], operand_names[0])
        elif op_type in [OperatorType.ADD_REAL, OperatorType.MUL_REAL]:
            op_char = " + " if op_type == OperatorType.ADD_REAL else " * "
            statement_str += op_char.join(operand_names)
        elif op_type in (
            [OperatorType.NUMBER, OperatorType.SYMBOL, OperatorType.MATRIX]):
            statement_str += operand_names[0]
        else:
            # Operators in which we do not know how to generate code
            raise Exception("Cannot generate code for operator %s" % op_type)
            
        statement_str += ";\n"
        file_handler.write(statement_str)
