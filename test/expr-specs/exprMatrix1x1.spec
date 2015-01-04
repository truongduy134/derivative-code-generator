/*************************************************
 * Expression to test that 1 x 1 Matrix should
 * be treated as a single number
 * (This feature is not supported in underlying computer algebra engine SYMPY)
 *************************************************/

const GOLDEN_RATIO = 1.618033
const SOME_CONST_V = [1, 2, 3, 4, 5]
const SOME_CONST_V_2 = [1, 1, 1, 1]

matrix A(4, 5)
vector v(5)
vector t(4)

expr main = t' * A * v + v' * SOME_CONST_V + GOLDEN_RATIO * (-SOME_CONST_V_2' * t)
