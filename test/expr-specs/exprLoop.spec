/********************************************************************
 * Expression that involves sum / product of many operands
 ********************************************************************/

number x

expr main =
  for j in [2, 20]
    sum(j + (for i in [1, 10] sum(i * x))) +
    for i in [10, 20]
      product(x + i)
// With loop variables i and j, we do not need to declare them
