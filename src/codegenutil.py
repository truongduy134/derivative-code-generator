from exprcodegen import VariableType

def get_java_func_declaration(
        func_name,
        ret_type,
        var_list):
    """ Gets a string which is a function / method declaration in Java.
        For example, "double foo(double x, double y)"
    Args:
        func_name : A string which is a name of the method / function
        ret_type : A string which is a return type of the method / function
        var_list : A list of Variable objects which are method parameters
    """
    param_str = ""
    is_first = True
    for var in var_list:
        if is_first:
            is_first = False
        else:
            param_str += ", "
        if var.var_type == VariableType.NUMBER:
            type_decl = "double"
        else:
            type_decl = "double" + "[]" * len(var.dimension)
        param_str += type_decl + " " + var.name
    func_delc = "%s %s(%s)" % (ret_type, func_name, param_str)
    return func_delc
