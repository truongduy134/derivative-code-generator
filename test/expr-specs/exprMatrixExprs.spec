/***********************************************************************
 * Expression that involves declaring a matrix whose elements are
 * arithmetic expressions themselves
 ***********************************************************************/

number x
number y
number z

expr main =
  [x, y - z, x + y + z]' *
  [[1, 2 + x, 3], [5 - y, z, 10 + x], [x * y, y - x * z, 1]] *
  [1, -z, 2 * y]
