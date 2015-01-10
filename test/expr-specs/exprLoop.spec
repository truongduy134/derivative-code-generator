/********************************************************************
 * Expression that involves sum / product of many operands
 ********************************************************************/

number x
number i : nodiff
number j : nodiff

expr main = for j in [2, 20] sum(j + (for i in [1, 10] sum(i * x))) +
  for i in [10, 20] product(x + i)
