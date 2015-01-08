""" The module contains fundamental definition of symbol variables and
    different symbol variable types
"""

class VariableType(object):
    """ An enum class for variable types (number, vector, or matrix)
    """
    (NUMBER,
     INTEGER,
     VECTOR,
     MATRIX) = range(4)

class Variable(object):
    """
    A class that encapsulates variable information

    Public object member attributes:
        name : A string representing name of a variable
        var_type : A VariableType enum value indicating variable type
        dimension : A tuple indicating dimension of a variable
    """

    def __init__(self, name, var_type, dimension):
        """ Class constructor
        """
        self.name = name
        self.var_type = var_type
        self.dimension = dimension
