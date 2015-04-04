/*************************************************************************
 * Expression with matrix and vector norm
 *************************************************************************/

const FIXED_LENGTH = 5

number L: nodiff        // Vector length
vector v(L): nodiff     // We cannot use v as differentiation variable since its length is variable
matrix m(FIXED_LENGTH, FIXED_LENGTH)      // Differentitation variable

expr main = norm(v) + norm(m)
