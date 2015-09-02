""" The module contains fundamental definition of symbol variables and
    different symbol variable types
"""

from collections import defaultdict


class VariableType(object):
    """ An enum class for variable types (number, vector, or matrix)
    """
    NUMBER = 0
    VECTOR = 1
    MATRIX = 2


class Variable(object):
    """
    A class that encapsulates variable information

    Public object member attributes:
        name : A string representing name of a variable
        var_type : A VariableType enum value indicating variable type
        dimension : A tuple indicating dimension of a variable
        props : A dictionary containing properties of this variable
    """

    def __init__(self, name, var_type, dimension, props=None):
        """ Class constructor
        """
        self.name = name
        self.var_type = var_type
        self.dimension = dimension
        if props:
            self.props = props
        else:
            self.props = defaultdict(bool)
