/***********************************************************************
 * Expression that involves declaring a vector whose elements are
 * arithmetic expressions themselves
 ***********************************************************************/

number X
number Y
number Z

expr main = [X - Y, X + Y, X * Y] . [X + Y, Y - X, Z]
