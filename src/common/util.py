"""
The module contains general-purpose utility functions
"""

def lower_first_char(my_str):
    if my_str:
        return my_str[:1].lower() + my_str[1:]
    return my_str
