/********************************************************************
 * Expression that involves sum / product of many operands
 ********************************************************************/

number n
number i
number j

expr main = for j in [2, 20] sum(j + (for i in [1, 10] sum(i * n))) +
  for i in [10, 20] product(n + i)
