/**
 * Simple expression with just real number arithmetics, and a vector with
 * equivalent property
 */

// Variable Declaration Section
// The order in which you declare variable is taken into account when
// generating function declaration
number x
number y
number z
vector v(5) : equivalent

// Main Expression Declaration Section
expr main = sqrt(ln(sin(y))) + x ^ (z + 2) + v[0]
