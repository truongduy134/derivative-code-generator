/**
 * Expression with some constant declarations
 */

const PI = 3.14
const IDENTITY2x2 = [[1, 0], [0, 1]]

number a
vector v(2)

expr main = a ^ PI + v . (IDENTITY2x2 * v)
