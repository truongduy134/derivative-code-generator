/***************************************************************************
 * Expression that has matrices with variable size
 ***************************************************************************/

number R : nodiff       // Matrix sizes are not differentiation variables
number C : nodiff
matrix M(R, C) : nodiff // Matrix with variable size
vector u(R) : nodiff
vector v(C) : nodiff
number x

expr main = u' * M * v * x
