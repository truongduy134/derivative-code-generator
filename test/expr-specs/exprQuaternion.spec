/**
 * Expression involved quaternion rotation
 *
 * Description: We are given two points P and Q, and a quaternion q.
 * Compute the distance between the image point of P by the rotation of q and
 * point Q
 */
vector q(4)                  // Assume this is a unit quaternion (x, y, z, w)

vector p(3) : nodiff         // Sample point (x, y, z)
vector imgP(3) : nodiff      // Transformed image point (x, y, z)

// Squared error function between the rotated image of p by quaternion q
// and the point imgP
expr main =
  // Error in x-coordinate
  ((1.0 - 2 * (q[1] ^ 2 + q[2] ^ 2)) * p[0] +
   2 * (q[0] * q[1] - q[2] * q[3]) * p[1] +
   2 * (q[0] * q[2] + q[1] * q[3]) * p[2] - imgP[0]) ^ 2 +
  // Error in y-coordinate
  (2 * (q[0] * q[1] + q[2] * q[3]) * p[0] +
   (1.0 - 2 * (q[0] ^ 2 + q[2] ^ 2)) * p[1] +
   2 * (q[1] * q[2] - q[0] * q[3]) * p[2] - imgP[1]) ^ 2 +
  // Error in z-coordinate
  (2 * (q[0] * q[2] - q[1] * q[3]) * p[0] +
   2 * (q[1] * q[2] + q[0] * q[3]) * p[1] +
   (1.0 - 2 * (q[0] ^ 2 + q[1] ^ 2)) * p[2] - imgP[2]) ^ 2
