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

class IndentType(object):
    """ An enum class for identation types (by space or by tab)
    """
    BY_SPACE = 0
    BY_TAB = 1

class FileCodeWriter(object):
    """ This class is a wrapper of normal file handler with writing mode.
        Instance of this class also takes care of code indentation when
        writing output code strings.

    Public object member attributes:
        tab_type : An IndentType enum indicating the generated code should be
                   indented by tab key or space
        tab_size : A integer indicating the tab size. The value is ignored if
                   indentation type is BY_TAB (i.e. tab key)

    Private object member attributes:
        __file_handler : An output file handler to write the code to
        __num_tab_from_margin : Number of tabs from the left margin
        __indent_str : A string that contains indentation characters that is
                       a prefix to a code line
    """

    DEFAULT_TAB_SIZE = 2
    DEFAULT_TAB_TYPE = IndentType.BY_SPACE

    def __init__(
            self,
            file_name,
            tab_type=None,
            tab_size=None):
        if tab_type is None:
            self.tab_type = FileCodeWriter.DEFAULT_TAB_TYPE
        else:
            self.tab_type = tab_type
        if tab_size is None:
            self.tab_size = FileCodeWriter.DEFAULT_TAB_SIZE
        else:
            self.tab_size = tab_size
        self.__file_handler = open(file_name, 'w')
        self.__num_tab_from_margin = 0
        self.__indent_str = self.__get_indent_string()

    def tab(self):
        """ Increases the number of tabs from left margin by 1
        """
        self.__num_tab_from_margin += 1
        self.__indent_str = self.__get_indent_string()

    def untab(self):
        """ Decreases the number of tabs from left margin by 1 if possible
        """
        if self.__num_tab_from_margin > 0:
            self.__num_tab_from_margin -= 1
            self.__indent_str = self.__get_indent_string()

    def write(self, content_str):
        """ Writes a content string to a file handler with a proper prefix
            indentation string
        Args:
            content_str : A string representing the content
        """
        self.__file_handler.write(self.__indent_str + content_str)

    def __get_indent_string(self):
        """ Gets indentation string for a code line
        Returns:
            a string contains indentation characters
        """
        if self.tab_type == IndentType.BY_TAB:
            return '\t' * self.__num_tab_from_margin
        return ' ' * (self.__num_tab_from_margin * self.tab_size)
