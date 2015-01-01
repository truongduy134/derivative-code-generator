/*******************
 * Expression that involves vector and matrix arithmetic
 *******************/

vector a(5)        // Declare a column vector with 5 rows
vector b(3)
matrix M(5, 3)     // Declare a matrix of size 5 x 3

expr main = b . (M' * a)
