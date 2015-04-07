/*************************************************************************
 * Expression with no differentiation variable
 *************************************************************************/

number N: nodiff
matrix M(N, N): nodiff

expr main = norm(M)
