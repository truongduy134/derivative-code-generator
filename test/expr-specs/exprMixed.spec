/*************************************************************************
 * Expression with mixed components
 *************************************************************************/

const PI = 3.14
const FIXED_LENGTH = 5

number L: nodiff        // Vector length
vector v(L): nodiff     // We cannot use v as differentiation variable since its length is variable
matrix m(FIXED_LENGTH, FIXED_LENGTH)      // Differentitation variable

expr main =
  (for i in [0, L - 1] sum(v[i])) *
  (for i in [0, FIXED_LENGTH - 1] for j in [0, FIXED_LENGTH - 1] sum(m[i][j])) +
  m[3][3] * v[0] ^ PI
