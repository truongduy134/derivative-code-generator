/**
 * Expression involved declaring sub-expressions
 *
 * This example is the same as the quaternion rotation example. The purpose is
 * to show that with sub-expressions, the specification becomes much cleaner
 *
 * Description: We are given two points P and Q, and a quaternion q.
 * Compute the distance between the image point of P by the rotation of q and
 * point Q
 */

vector q(4)                  // Assume this is a unit quaternion (x, y, z, w)

vector p(3) : nodiff         // Sample point (x, y, z)
vector imgP(3) : nodiff      // Transformed image point (x, y, z)

matrix T(3, 3)

expr rotationMatrix =
  [[1.0 - 2 * (q[1] ^ 2 + q[2] ^ 2), 2 * (q[0] * q[1] - q[2] * q[3]), 2 * (q[0] * q[2] + q[1] * q[3])],
   [2 * (q[0] * q[1] + q[2] * q[3]), 1.0 - 2 * (q[0] ^ 2 + q[2] ^ 2), 2 * (q[1] * q[2] - q[0] * q[3])],
   [2 * (q[0] * q[2] - q[1] * q[3]), 2 * (q[1] * q[2] + q[0] * q[3]), 1.0 - 2 * (q[0] ^ 2 + q[1] ^ 2)]]

expr rotatedPoint = rotationMatrix * T * p

// Squared error function between the rotated image of p by quaternion q
// and the point imgP
expr main =
  // Error in x-coordinate
  (rotatedPoint[0] - imgP[0]) ^ 2 +
  // Error in y-coordinate
  (rotatedPoint[1] - imgP[1]) ^ 2 +
  // Error in z-coordinate
  (rotatedPoint[2] - imgP[2]) ^ 2
